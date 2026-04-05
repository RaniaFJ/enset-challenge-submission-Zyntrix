"""
Logistics routing - decides where products go based on quality
"""


def logistique_agent(state: dict) -> dict:
    # routes based on quality status and score
    
    status = state.get('quality_status', 'GOOD')
    score = state.get('quality_score', 0)
    
    if status == "BAD":
        route = "REROUTED_TO_QUARANTINE"
        actions = ["block", "inspect", "isolate", "notify", "document"]
    elif score >= 0.45:
        route = "PRIORITY_COLD_CHAIN"
        actions = ["prioritize", "monitor", "alert_team", "prepare_contingency"]
    else:
        route = "NORMAL_DELIVERY"
        actions = ["keep_route", "standard_monitoring", "log_compliant"]
    
    state['route'] = route
    state['logistics_actions'] = actions
    
    return state
