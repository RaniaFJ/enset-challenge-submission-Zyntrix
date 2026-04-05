"""
Alert generation - creates alerts and finds similar historical cases
"""

from rag import SimpleRAG


def alertes_agent(state: dict) -> dict:
    # gen alerts based on quality score and metrics
    
    alerts = []
    q_score = state.get('quality_score', 0)
    temp = state.get('temperature', 0)
    humid = state.get('humidity', 0)
    text = (state.get('text_report') or '').lower()
    visual = (state.get('visual_report') or '').lower()
    
    # quality-based alerts
    if q_score >= 0.8:
        alerts.append("CRITICAL: Product quality severely compromised")
    elif q_score >= 0.6:
        alerts.append("WARNING: Product quality at risk")
    else:
        alerts.append("CAUTION: Product quality concerns detected")
    
    # temp alerts
    if temp > 25:
        alerts.append(f"ALERT: Temperature high ({temp}°C)")
    elif temp < 2:
        alerts.append(f"ALERT: Temperature too low ({temp}°C)")
    
    # humidity alerts
    if humid > 95:
        alerts.append(f"ALERT: Humidity critical ({humid}%)")
    elif humid < 70:
        alerts.append(f"ALERT: Humidity low ({humid}%)")
    
    # text analysis
    if 'contamination' in text:
        alerts.append("CRITICAL: Contamination detected")
    if 'mold' in text:
        alerts.append("CRITICAL: Mold detected")
    if 'spoilage' in text:
        alerts.append("WARNING: Spoilage indicators present")
    
    # visual analysis
    if 'leak' in visual:
        alerts.append("CRITICAL: Package leak detected")
    if 'broken' in visual:
        alerts.append("WARNING: Package damage detected")
    if 'fungus' in visual:
        alerts.append("CRITICAL: Fungal growth detected")
    
    # get similar cases from memory
    similar = []
    try:
        rag_inst = state.get('_rag_instance')
        if rag_inst:
            similar = rag_inst.retrieve_similar(state, k=3)
    except Exception as e:
        print(f"rag lookup failed: {e}")
    
    alert_str = " | ".join(alerts)
    
    state['alerts'] = alerts
    state['similar_cases'] = similar
    state['alert'] = alert_str
    
    return state
