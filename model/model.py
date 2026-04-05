"""
Quality prediction interface - loads model and makes predictions
"""

import joblib
from pathlib import Path

# load models at startup
_model_dir = Path(__file__).parent
_model = joblib.load(_model_dir / 'quality_model.pkl')
_encoder = joblib.load(_model_dir / 'fruit_encoder.pkl')


def predict_quality(temp, humidity, co2, light=300, fruit="Tomato"):
    # predict quality (GOOD/BAD) for given sensor values
    
    try:
        # encode fruit name
        try:
            fruit_enc = _encoder.transform([fruit])[0]
        except (ValueError, KeyError):
            # fallback if fruit not in training
            fruit_enc = 0
        
        # prepare features
        features = [[temp, humidity, light, co2, fruit_enc]]
        
        # predict
        pred = _model.predict(features)[0]
        proba = _model.predict_proba(features)[0]
        
        status = "BAD" if pred == 1 else "GOOD"
        conf = float(proba[pred])
        ml_risk = 0.5 if pred == 1 else 0.0
        
        return {
            "status": status,
            "confidence": conf,
            "ml_risk": ml_risk
        }
    
    except Exception as e:
        # something went wrong, default to good
        print(f"prediction error: {e}")
        return {
            "status": "GOOD",
            "confidence": 0.0,
            "ml_risk": 0.0
        }
