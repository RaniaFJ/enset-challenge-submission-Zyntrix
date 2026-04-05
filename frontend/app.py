import streamlit as st
import requests
import time
from datetime import datetime

# session defaults
defaults = {
    "batch_id": "BATCH_2024_001",
    "temperature": 5.0,
    "humidity": 60,
    "location": "",
    "product_type": "Tomato",
    "text_report": "",
    "visual_report": "",
    "vibration": 2.0,
    "co2": 400,
    "delay_hours": 0.0,
    "result": None
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# theme and page config
st.set_page_config(
    page_title="Zyntrix — Quality Control",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

* { font-family: 'Syne', sans-serif !important; }
.stApp { background-color: #0a0f0d !important; }
section[data-testid="stSidebar"] { display: none; }

/* Hide streamlit default elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 1100px; }

/* Input fields */
input[type="text"], input[type="number"], textarea {
  background: #142019 !important;
  border: 1px solid #3a5045 !important;
  border-radius: 2px !important;
  color: #c8e8d4 !important;
  font-family: 'Space Mono', monospace !important;
  font-size: 12px !important;
}
input:focus, textarea:focus {
  border-color: #00ff88 !important;
  box-shadow: none !important;
}

/* Labels */
label { 
  color: #6a9a7a !important; 
  font-size: 10px !important; 
  font-weight: 700 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
}

/* Buttons */
.stButton > button {
  background: #00ff88 !important;
  color: #000 !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 800 !important;
  font-size: 13px !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  border: none !important;
  border-radius: 2px !important;
  width: 100% !important;
  padding: 14px !important;
}
.stButton > button:hover { background: #00cc6a !important; }

/* Preset buttons — smaller */
.preset-btn > button {
  background: transparent !important;
  color: #6a9a7a !important;
  border: 1px solid #3a5045 !important;
  font-size: 10px !important;
  padding: 5px 12px !important;
  width: auto !important;
}
.preset-btn > button:hover {
  border-color: #00ff88 !important;
  color: #00ff88 !important;
}

/* Cards via st.container / st.markdown */
.panel {
  background: #0f1a14;
  border: 1px solid #3a5045;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 20px;
}
.panel-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #00ff88;
  text-transform: uppercase;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-left: 3px solid #00ff88;
  padding-left: 8px;
}

/* Agent rows */
.agent-row {
  background: #0f1a14;
  border: 1px solid #3a5045;
  border-radius: 4px;
  padding: 14px 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 8px;
}
.agent-row.active { border-color: #00ff88; box-shadow: 0 0 20px rgba(0,255,136,0.08); }
.agent-row.skipped { opacity: 0.35; }

.agent-name {
  font-family: 'Space Mono', monospace;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #c8e8d4;
}
.agent-desc { font-size: 11px; color: #6a9a7a; font-family: 'Space Mono', monospace; }

.status-waiting { background: rgba(58,80,69,0.5); color: #6a9a7a; padding: 3px 8px; border-radius: 2px; font-size: 10px; font-family: 'Space Mono', monospace; }
.status-running { background: rgba(0,255,136,0.15); color: #00ff88; padding: 3px 8px; border-radius: 2px; font-size: 10px; font-family: 'Space Mono', monospace; }
.status-done { background: rgba(0,255,136,0.1); color: #00cc6a; padding: 3px 8px; border-radius: 2px; font-size: 10px; font-family: 'Space Mono', monospace; }
.status-skipped { border: 1px solid #3a5045; color: #3a5045; padding: 3px 8px; border-radius: 2px; font-size: 10px; font-family: 'Space Mono', monospace; }

/* Result cards */
.result-card {
  background: #0f1a14;
  border: 1px solid #3a5045;
  border-radius: 4px;
  padding: 18px;
  margin-bottom: 12px;
}
.result-card.bad { border-color: #ff4444; }
.result-card.warn { border-color: #ffb830; }
.result-card.good { border-color: #00ff88; }

.verdict-label { font-size: 10px; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; color: #6a9a7a; margin-bottom: 8px; }
.verdict-bad { font-size: 28px; font-weight: 800; color: #ff4444; }
.verdict-warn { font-size: 28px; font-weight: 800; color: #ffb830; }
.verdict-good { font-size: 28px; font-weight: 800; color: #00ff88; }

.route-quarantine { background: rgba(255,68,68,0.15); color: #ff4444; border: 1px solid #ff4444; padding: 6px 12px; border-radius: 2px; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; display: inline-block; margin-top: 8px; }
.route-cold { background: rgba(255,184,48,0.15); color: #ffb830; border: 1px solid #ffb830; padding: 6px 12px; border-radius: 2px; font-size: 11px; font-weight: 700; display: inline-block; margin-top: 8px; }
.route-normal { background: rgba(0,255,136,0.1); color: #00ff88; border: 1px solid #00ff88; padding: 6px 12px; border-radius: 2px; font-size: 11px; font-weight: 700; display: inline-block; margin-top: 8px; }

.alert-item { font-family: 'Space Mono', monospace; font-size: 10px; color: #ffb830; padding: 6px 10px; background: rgba(255,184,48,0.07); border-left: 2px solid #ffb830; margin-bottom: 4px; }
.action-item { font-family: 'Space Mono', monospace; font-size: 10px; color: #c8e8d4; padding: 6px 10px; background: #142019; border-left: 2px solid #3a5045; margin-bottom: 4px; }
.case-item { font-family: 'Space Mono', monospace; font-size: 10px; color: #4af0ff; padding: 6px 10px; background: rgba(74,240,255,0.05); border-left: 2px solid #4af0ff; margin-bottom: 4px; }
.trace-box { font-family: 'Space Mono', monospace; font-size: 10px; color: #6a9a7a; background: #142019; border: 1px solid #3a5045; border-radius: 2px; padding: 12px; line-height: 1.8; word-break: break-all; }

.score-bar-bg { height: 4px; background: #142019; border-radius: 2px; margin-top: 10px; }
.score-bar-fill-bad { height: 4px; background: #ff4444; border-radius: 2px; }
.score-bar-fill-warn { height: 4px; background: #ffb830; border-radius: 2px; }
.score-bar-fill-good { height: 4px; background: #00ff88; border-radius: 2px; }

.reasoning-box { font-family: 'Space Mono', monospace; font-size: 10px; color: #6a9a7a; line-height: 1.8; }

.enset-bar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 14px;
  background: rgba(0,255,136,0.04);
  border: 1px solid rgba(0,255,136,0.15);
  border-radius: 2px;
  margin-bottom: 28px;
  font-family: 'Space Mono', monospace;
  font-size: 11px;
  color: #6a9a7a;
}
</style>
""", unsafe_allow_html=True)

# header
st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:32px">
  <div style="display:flex;align-items:center;gap:12px">
    <div style="width:10px;height:10px;border-radius:50%;background:#00ff88;box-shadow:0 0 12px #00ff88"></div>
    <span style="font-size:13px;font-weight:700;letter-spacing:0.15em;color:#00ff88;text-transform:uppercase">Zyntrix</span>
  </div>
  <span style="font-family:'Space Mono',monospace;font-size:10px;color:#6a9a7a;border:1px solid #3a5045;padding:4px 10px;border-radius:2px">v1.0 · IA Agentique</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="enset-bar">
  <span>🏆 <strong style="color:#00ff88">ENSET Challenge 2026</strong> — Hackathon IA Agentique</span>
  <span>Industrie 4.0 · Supply Chain</span>
</div>
""", unsafe_allow_html=True)

# title and intro
st.markdown("""
<div style="margin-bottom:36px">
  <h1 style="font-size:clamp(28px,5vw,46px);font-weight:800;line-height:1.1;letter-spacing:-0.02em;color:#c8e8d4">
    Agricultural<br/><span style="color:#00ff88">Quality Control</span><br/>Agent System
  </h1>
  <p style="margin-top:10px;color:#6a9a7a;font-size:14px;max-width:500px;line-height:1.6">
    Multi-agent pipeline that autonomously assesses batch quality, generates alerts, 
    optimizes logistics routing, and builds an immutable audit trail.
  </p>
</div>
""", unsafe_allow_html=True)

# preset buttons
preset_col1, preset_col2, preset_col3 = st.columns(3, gap="small")

with preset_col1:
    if st.button("🔴 Critical", key="preset_critical"):
        st.session_state.batch_id = "BATCH_2024_013"
        st.session_state.temperature = 14.5
        st.session_state.humidity = 88
        st.session_state.location = "Souk Sebt Storage"
        st.session_state.product_type = "Strawberries"
        st.session_state.text_report = "Strong odour detected, contamination near pallet 3"
        st.session_state.visual_report = "Fungus growth on 20% of items, leaking boxes"
        st.session_state.vibration = 9.8
        st.session_state.co2 = 1200
        st.session_state.delay_hours = 8
        st.rerun()

with preset_col2:
    if st.button("🟡 Borderline", key="preset_borderline"):
        st.session_state.batch_id = "BATCH_2024_027"
        st.session_state.temperature = 8.5
        st.session_state.humidity = 74
        st.session_state.location = "Agadir Port Hub"
        st.session_state.product_type = "Tomato"
        st.session_state.text_report = "Slight odour on arrival, packaging intact"
        st.session_state.visual_report = "Minor bruise on 8% of items"
        st.session_state.vibration = 5.2
        st.session_state.co2 = 820
        st.session_state.delay_hours = 3
        st.rerun()

with preset_col3:
    if st.button("🟢 Good", key="preset_clean"):
        st.session_state.batch_id = "BATCH_2024_041"
        st.session_state.temperature = 5.0
        st.session_state.humidity = 60
        st.session_state.location = "Casablanca Cold Chain"
        st.session_state.product_type = "Citrus"
        st.session_state.text_report = "No issues detected"
        st.session_state.visual_report = "No visible damage"
        st.session_state.vibration = 2.1
        st.session_state.co2 = 450
        st.session_state.delay_hours = 0.5
        st.rerun()

st.markdown('<div class="panel"><div class="panel-title">Batch Input</div></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="small")
with col1:
    st.session_state.batch_id = st.text_input(
        "Batch ID",
        value=st.session_state.batch_id,
        key="batch_id_input"
    )
with col2:
    st.session_state.product_type = st.text_input(
        "Product Type",
        value=st.session_state.product_type,
        key="product_type_input"
    )
with col3:
    st.session_state.location = st.text_input(
        "Location",
        value=st.session_state.location,
        key="location_input"
    )

col1, col2, col3, col4, col5 = st.columns(5, gap="small")
with col1:
    st.session_state.temperature = st.number_input(
        "Temperature (°C)",
        value=st.session_state.temperature,
        step=0.1,
        key="temp_input"
    )
with col2:
    st.session_state.humidity = st.number_input(
        "Humidity (%)",
        value=int(st.session_state.humidity),
        min_value=30,
        max_value=100,
        step=1,
        key="humidity_input"
    )
with col3:
    st.session_state.vibration = st.number_input(
        "Vibration (m/s²)",
        value=st.session_state.vibration,
        step=0.1,
        key="vibration_input"
    )
with col4:
    st.session_state.co2 = st.number_input(
        "CO₂ (ppm)",
        value=st.session_state.co2,
        step=1,
        key="co2_input"
    )
with col5:
    st.session_state.delay_hours = st.number_input(
        "Delay (hours)",
        value=st.session_state.delay_hours,
        step=0.1,
        key="delay_input"
    )

col1, col2 = st.columns(2, gap="small")
with col1:
    st.session_state.text_report = st.text_input(
        "Text Report (Optional)",
        value=st.session_state.text_report,
        key="text_report_input"
    )
with col2:
    st.session_state.visual_report = st.text_input(
        "Visual Report (Optional)",
        value=st.session_state.visual_report,
        key="visual_report_input"
    )

st.markdown("<br/>", unsafe_allow_html=True)

# analyze button
analyze_clicked = st.button("▶  ANALYZE BATCH", key="analyze_btn")

if analyze_clicked:
    agent_data = [
        ("⚙", "Normalize", "Validate inputs & set defaults", "#4af0ff"),
        ("🔬", "Qualité Agent", "ML + NLP + Vision + Metrics analysis", "#00ff88"),
        ("⚠", "Alertes Agent", "Alert generation + RAG memory retrieval", "#ffb830"),
        ("🚛", "Logistique Agent", "Route optimization & action planning", "#ff4444"),
        ("🔗", "Tracabilité Agent", "Blockchain-ready audit trail", "#4af0ff"),
    ]
    
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    st.markdown('<div class="panel-title" style="margin-bottom:20px">Agent Pipeline</div>', unsafe_allow_html=True)
    
    # Create placeholders for each agent
    agent_placeholders = [st.empty() for _ in range(len(agent_data))]
    
    # animate steps
    for idx, (icon, name, desc, color) in enumerate(agent_data):
        agent_placeholders[idx].markdown(f"""
<div class="agent-row active">
  <div style="width:32px;height:32px;border-radius:2px;background:{color}18;color:{color};display:flex;align-items:center;justify-content:center;font-size:14px">{icon}</div>
  <div style="flex:1">
    <div class="agent-name" style="color:{color}">{name}</div>
    <div class="agent-desc">{desc}</div>
  </div>
  <span class="status-running">RUNNING</span>
</div>
        """, unsafe_allow_html=True)
        
        time.sleep(0.4)
        
        # mark as done
        agent_placeholders[idx].markdown(f"""
<div class="agent-row active">
  <div style="width:32px;height:32px;border-radius:2px;background:{color}18;color:{color};display:flex;align-items:center;justify-content:center;font-size:14px">{icon}</div>
  <div style="flex:1">
    <div class="agent-name" style="color:{color}">{name}</div>
    <div class="agent-desc">{desc}</div>
  </div>
  <span class="status-done">DONE</span>
</div>
        """, unsafe_allow_html=True)
    
    # send to backend
    try:
        payload = {
            "batch_id": st.session_state.batch_id,
            "temperature": st.session_state.temperature,
            "humidity": st.session_state.humidity,
            "location": st.session_state.location,
            "product_type": st.session_state.product_type,
            "text_report": st.session_state.get("text_report", ""),
            "visual_report": st.session_state.get("visual_report", ""),
            "industrial_metrics": {
                "vibration": st.session_state.vibration,
                "co2": st.session_state.co2,
                "delay_hours": st.session_state.delay_hours
            }
        }
        
        response = requests.post(
            "http://localhost:8000/analyze",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        st.session_state.result = result
        
    except requests.exceptions.ConnectionError:
        st.markdown("""
<div class="result-card bad">
  <div class="verdict-label">Connection Error</div>
  <div style="color:#ff4444;font-size:12px">Unable to connect to backend. Ensure FastAPI server is running on http://localhost:8000</div>
</div>
        """, unsafe_allow_html=True)
        st.session_state.result = None
    except requests.exceptions.Timeout:
        st.markdown("""
<div class="result-card bad">
  <div class="verdict-label">Timeout</div>
  <div style="color:#ff4444;font-size:12px">Analysis took too long. Try again or check backend performance.</div>
</div>
        """, unsafe_allow_html=True)
        st.session_state.result = None
    except Exception as e:
        st.markdown(f"""
<div class="result-card bad">
  <div class="verdict-label">Error</div>
  <div style="color:#ff4444;font-size:12px">{str(e)}</div>
</div>
        """, unsafe_allow_html=True)
        st.session_state.result = None

if st.session_state.result:
    result = st.session_state.result
    
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    st.markdown('<div class="panel-title" style="margin-bottom:20px">Results</div>', unsafe_allow_html=True)
    
    quality_score = result.get("quality_score", 0.0)
    quality_status = result.get("quality_status", "UNKNOWN")
    route = result.get("route", "NORMAL_DELIVERY")
    reasoning = result.get("reasoning", "")
    alerts = result.get("alerts", [])
    similar_cases = result.get("similar_cases", [])
    trace = result.get("trace", "")
    logistics_actions = result.get("logistics_actions", [])
    
    # verdict colors
    verdict_key = "bad" if quality_status == "BAD" else ("warn" if quality_score >= 0.45 else "good")
    verdict_text = "🔴 CRITICAL" if quality_status == "BAD" else ("🟡 WARNING" if quality_score >= 0.45 else "🟢 COMPLIANT")
    result_card_class = verdict_key
    fill_class = verdict_key
    
    # route class
    if "QUARANTINE" in route:
        route_class = "quarantine"
        route_text = "🚫 REROUTED TO QUARANTINE"
    elif "PRIORITY" in route or "COLD_CHAIN" in route:
        route_class = "cold"
        route_text = "⚠ PRIORITY COLD CHAIN"
    else:
        route_class = "normal"
        route_text = "✓ NORMAL DELIVERY"
    
    st.markdown(f"""
<div class="result-card {result_card_class}">
  <div class="verdict-label">Quality Verdict</div>
  <div class="verdict-{verdict_key}">{verdict_text}</div>
  <div style="margin-top:8px;font-size:12px;color:#6a9a7a;font-family:'Space Mono',monospace">Score: {quality_score:.3f}</div>
  <div class="score-bar-bg"><div class="score-bar-fill-{fill_class}" style="width:{quality_score*100:.1f}%"></div></div>
  <div style="margin-top:12px">
    <div class="verdict-label">Route Decision</div>
    <span class="route-{route_class}">{route_text}</span>
  </div>
</div>
    """, unsafe_allow_html=True)
    
    # reasoning
    if reasoning:
        reasoning_html = reasoning.replace("\n", "<br/>")
        st.markdown(f"""
<div class="result-card">
  <div class="verdict-label">AI Reasoning</div>
  <div class="reasoning-box">{reasoning_html}</div>
</div>
        """, unsafe_allow_html=True)
    
    if alerts:
        alerts_html = "".join([f'<div class="alert-item">{alert}</div>' for alert in alerts])
        st.markdown(f"""
<div class="result-card warn">
  <div class="verdict-label">Active Alerts</div>
  {alerts_html}
</div>
        """, unsafe_allow_html=True)
    
    if logistics_actions:
        actions_html = "".join([f'<div class="action-item">→ {action}</div>' for action in logistics_actions])
        st.markdown(f"""
<div class="result-card">
  <div class="verdict-label">Logistics Actions</div>
  {actions_html}
</div>
        """, unsafe_allow_html=True)
    
    if similar_cases:
        cases_html = "".join([f'<div class="case-item">{case}</div>' for case in similar_cases])
        st.markdown(f"""
<div class="result-card">
  <div class="verdict-label">Similar Cases</div>
  {cases_html}
</div>
        """, unsafe_allow_html=True)
    
    if trace:
        timestamp = datetime.utcnow().isoformat() + "Z"
        trace_html = trace.replace("\n", "<br/>").replace(" → ", " <strong>→</strong> ")
        st.markdown(f"""
<div class="result-card">
  <div class="verdict-label">Audit Trail</div>
  <div class="trace-box">{trace_html}</div>
  <div style="margin-top:8px;font-size:10px;color:#6a9a7a;font-family:'Space Mono',monospace">UTC: {timestamp}</div>
</div>
        """, unsafe_allow_html=True)
