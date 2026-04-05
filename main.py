"""
FastAPI app for cold storage quality monitoring.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from graph import create_app
from rag import SimpleRAG


class AnalysisRequest(BaseModel):
    batch_id: str
    temperature: float
    humidity: float
    location: str
    product_type: str
    text_report: str = ""
    visual_report: str = ""
    industrial_metrics: dict = None


class AnalysisResponse(BaseModel):
    batch_id: str
    quality_status: str
    quality_score: float
    route: str
    alerts: list
    timestamp: str


app = FastAPI(title="Cold Storage Quality Monitor")

# init RAG and graph
rag = SimpleRAG()
graph = create_app(rag_instance=rag)

# setup logging
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / 'logs.txt'


@app.get('/health')
def health():
    # just a health check
    return {"status": "ok"}


@app.get('/memory')
def get_memory():
    # return how many cases we've stored
    return {
        "memory_count": len(rag.memory_texts),
        "stored_cases": len(rag.memory_texts)
    }


@app.post('/analyze')
def analyze(req: AnalysisRequest) -> dict:
    # main analysis endpoint
    
    state = {
        'batch_id': req.batch_id,
        'temperature': req.temperature,
        'humidity': req.humidity,
        'location': req.location,
        'product_type': req.product_type,
        'text_report': req.text_report,
        'visual_report': req.visual_report,
        'light': 300,
        'co2': 0,
        'industrial_metrics': req.industrial_metrics or {}
    }
    
    # extract co2 from metrics if passed
    if req.industrial_metrics and 'co2' in req.industrial_metrics:
        state['co2'] = req.industrial_metrics['co2']
    
    # run the analysis
    result = graph.run(state)
    
    # store in memory for rag
    rag.store(result)
    
    # log to file
    log_entry = json.dumps({
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'batch_id': req.batch_id,
        'quality_status': result.get('quality_status'),
        'quality_score': result.get('quality_score'),
        'route': result.get('route'),
        'alerts': result.get('alerts', [])
    })
    
    try:
        with open(log_file, 'a') as f:
            f.write(log_entry + '\n')
    except IOError as e:
        print(f"couldn't write log: {e}")
    
    # clean non-serializable stuff before returning
    res = result.copy()
    res.pop('_rag_instance', None)
    res.pop('ml_result', None)
    
    return res


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
