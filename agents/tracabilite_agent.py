"""
Traceability - builds supply chain record
"""

from datetime import datetime, timezone


def tracabilite_agent(state: dict) -> dict:
    # build trace record for audit trail
    
    ts = datetime.now(timezone.utc).isoformat()
    
    batch = state.get('batch_id', 'UNKNOWN')
    prod = state.get('product_type', 'UNKNOWN')
    loc = state.get('location', 'UNKNOWN')
    status = state.get('quality_status', 'UNKNOWN')
    route = state.get('route', 'UNKNOWN')
    
    # main trace string
    trace_str = (
        f"batch={batch} → "
        f"product={prod} → "
        f"origin={loc} → "
        f"quality={status} → "
        f"route={route} → "
        f"ts={ts}"
    )
    
    # trace chain (each element)
    chain = [
        f"batch={batch}",
        f"product={prod}",
        f"origin={loc}",
        f"quality={status}",
        f"route={route}",
        f"ts={ts}"
    ]
    
    state['trace'] = trace_str
    state['trace_chain'] = chain
    state['timestamp'] = ts
    
    return state
