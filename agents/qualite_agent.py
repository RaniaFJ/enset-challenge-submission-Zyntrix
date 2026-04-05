"""
Quality assessment - combines ML + text + visual + process metrics
"""

from model.model import predict_quality


def qualite_agent(state: dict) -> dict:
    # get ML prediction
    ml = predict_quality(
        temp=state.get('temperature', 0),
        humidity=state.get('humidity', 0),
        co2=state.get('co2', 0),
        light=state.get('light', 300),
        fruit=state.get('product_type', 'Tomato')
    )
    ml_risk = ml['ml_risk']
    
    # check text for bad stuff
    text = (state.get('text_report') or '').lower()
    text_kw = ['contamination', 'mold', 'odour', 'spoilage', 'damage']
    text_hits = sum(1 for kw in text_kw if kw in text)
    text_risk = min(text_hits * 0.15, 0.30)
    
    # check visual report
    visual = (state.get('visual_report') or '').lower()
    visual_kw = ['bruise', 'leak', 'broken', 'stain', 'fungus']
    visual_hits = sum(1 for kw in visual_kw if kw in visual)
    visual_risk = min(visual_hits * 0.12, 0.25)
    
    # process metrics stuff
    proc_risk = 0.0
    metrics = state.get('industrial_metrics') or {}
    
    if metrics.get('vibration', 0) > 7:
        proc_risk += 0.05
    if metrics.get('co2', state.get('co2', 0)) > 1000:
        proc_risk += 0.05
    if metrics.get('delay_hours', 0) > 5:
        proc_risk += 0.05
    
    # calc final score
    q_score = min(ml_risk + text_risk + visual_risk + proc_risk, 1.0)
    q_status = "BAD" if q_score >= 0.5 else "GOOD"
    
    reason = (
        f"ML: {ml_risk:.2f} | "
        f"Text: {text_risk:.2f} ({text_hits} hits) | "
        f"Visual: {visual_risk:.2f} ({visual_hits} hits) | "
        f"Process: {proc_risk:.2f} | "
        f"Total: {q_score:.2f} → {q_status}"
    )
    
    state['quality_score'] = q_score
    state['quality_status'] = q_status
    state['reasoning_quality'] = reason
    state['ml_result'] = ml
    
    return state
