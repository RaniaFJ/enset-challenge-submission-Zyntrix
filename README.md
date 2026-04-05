# Cold Storage Quality Monitoring System

*IoT-powered quality assurance for cold logistics. ML-driven batch analysis with intelligent routing and full traceability.*

---

## Features

| Feature | Description |
|---------|-------------|
| **ML Quality Prediction** | RandomForest classifier on 10K+ sensor readings |
| **Multi-Signal Fusion** | Sensor data + NLP + visual inspection + process metrics |
| **Smart Routing** | Auto-classify into quarantine, priority, or normal paths |
| **Historical RAG** | Retrieve similar cases for context and precedent |
| **Supply Chain Trace** | ISO8601 timestamps with full audit trail |
| **REST API** | FastAPI backend with integrated frontend |

---

## Project Structure

```
hacka/
├── frontend/              ← Streamlit dashboard (localhost:8501)
├── model/
│   ├── train.py          ← Generate RandomForest + encoders
│   └── model.py          ← Prediction interface
├── agents/               ← Multi-agent analysis pipeline
│   ├── qualite_agent.py
│   ├── alertes_agent.py
│   ├── logistique_agent.py
│   └── tracabilite_agent.py
├── data/
│   └── cold_storage_data.csv
├── logs/logs.txt         ← Audit trail (JSON lines)
├── rag.py                ← Similarity search engine
├── graph.py              ← State graph orchestration
├── main.py               ← FastAPI server (localhost:8000)
└── requirements.txt
```

---

## Setup

```bash
pip install -r requirements.txt
python model/train.py
python main.py
```

API runs on `http://localhost:8000`

---

## Frontend

```bash
streamlit run frontend/app.py
```

Dashboard runs on `http://localhost:8501`

**Required:** Ensure the API (main.py) is running before starting the frontend.

---

## API Endpoint

### POST /analyze

Analyze cold storage batch quality.

**Request:**

```json
{
  "batch_id": "BATCH_20250405_001",
  "temperature": 4.5,
  "humidity": 85,
  "location": "Agadir Cold Hub",
  "product_type": "Tomato",
  "text_report": "Routine inspection OK",
  "visual_report": "No damage",
  "industrial_metrics": {
    "vibration": 3.2,
    "co2": 450,
    "delay_hours": 2.5
  }
}
```

**Response:**

```json
{
  "batch_id": "BATCH_20250405_001",
  "quality_status": "GOOD",
  "quality_score": 0.15,
  "route": "NORMAL_DELIVERY",
  "alerts": [],
  "trace": "BATCH_20250405_001 | Tomato | GOOD | NORMAL_DELIVERY"
}
```

---

## Analysis Pipeline

```
INPUT: Batch Data (sensors, reports, metrics)
   |
   v
[normalize] Set defaults for all fields
   |
   v
[qualite] ML + NLP + visual + process risk assessment
   |
   +------- risk detected (score >= 0.45)?
   |
   +--YES--> [alertes] Generate warnings, retrieve similar cases
   |         |
   +--NO---> |
            |
            v
         [logistique] Route decision (QUARANTINE / PRIORITY / NORMAL)
            |
            v
         [tracabilite] Log with ISO8601 timestamp + full trace
            |
            v
         OUTPUT: JSON response with all analysis fields
```

---

## Quality Scoring

The system fuses four independent risk signals into a composite quality score:

```
quality_score = ml_risk + text_risk + visual_risk + process_risk
                (each capped per component, sum ≤ 1.0)
```

| Signal | Max | Source | Triggers |
|--------|-----|--------|----------|
| **ML Risk** | 0.5 | RandomForest classifier | Model predicts BAD state |
| **Text Risk** | 0.30 | NLP keyword scan | contamination, mold, spoilage, damage |
| **Visual Risk** | 0.25 | Report text parsing | bruise, leak, broken, stain, fungus |
| **Process Risk** | 0.15 | Industrial metrics | vibration > 7 OR CO2 > 1000 OR delay > 5h |

### Routing Decision Table

```
quality_score < 0.45      → NORMAL_DELIVERY      (green)
0.45 <= score < 0.50      → PRIORITY_COLD_CHAIN  (orange)
status == "BAD"           → QUARANTINE           (red)
```

| Route | Logic | Actions |
|-------|-------|---------|
| NORMAL | Low risk | Keep standard route, standard monitoring |
| PRIORITY | Medium risk | Monitor closely, alert team |
| QUARANTINE | High risk | Hold batch, inspect, isolate, notify |

---



## Dataset

**Source:** [Mendeley Cold Storage IoT Dataset](https://data.mendeley.com/datasets/czz68d9fwj/1) (CC BY 4.0)

```
10,996 real sensor readings from cold storage facilities

Features:
  - Temperature (°C)
  - Humidity (%)
  - CO2 (ppm)
  - Light intensity
  - Fruit type (categorical)

Target:
  - Binary label: Good / Bad
  
Split:
  - 80% training
  - 20% test
```

---

## Implementation Notes

- **Architecture**: Custom state graph (no external framework like langgraph/crewai)
- **Agents**: Pure functions with `(state: dict) -> dict` signature
- **Retrieval**: RAG uses Jaccard similarity for case matching
- **Audit Trail**: JSON-lines format appended to logs/logs.txt
- **Model**: RandomForest with 100 estimators, max_depth=15
- **Serialization**: joblib for .pkl model files

---
