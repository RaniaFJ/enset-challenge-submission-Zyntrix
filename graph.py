"""
Custom state graph - runs agents in sequence with conditional routing
(no external frameworks, just pure python)
"""

from agents.qualite_agent import qualite_agent
from agents.alertes_agent import alertes_agent
from agents.logistique_agent import logistique_agent
from agents.tracabilite_agent import tracabilite_agent


class StateGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.conditional_edges = {}
        self.entry_point = None
    
    def add_node(self, name: str, func):
        # add a node (agent function)
        self.nodes[name] = func
    
    def add_edge(self, src: str, dst: str):
        # direct edge between nodes
        self.edges.append((src, dst))
    
    def add_conditional_edge(self, src: str, cond_fn, dst_map: dict):
        # conditional routing - cond_fn returns key -> lookup in dst_map
        self.conditional_edges[src] = (cond_fn, dst_map)
    
    def set_entry_point(self, node: str):
        self.entry_point = node
    
    def run(self, init_state: dict) -> dict:
        # execute the graph
        state = init_state.copy()
        current = self.entry_point
        visited = set()
        
        while current and current not in visited:
            visited.add(current)
            
            # run the node
            if current in self.nodes:
                state = self.nodes[current](state)
            
            # find next node
            current = self._next_node(current, state)
        
        return state
    
    def _next_node(self, curr: str, state: dict):
        # determine which node to run next
        
        # check conditional edges first
        if curr in self.conditional_edges:
            cond_fn, dst_map = self.conditional_edges[curr]
            decision = cond_fn(state)
            next_node = dst_map.get(decision)
            if next_node:
                return next_node
        
        # check direct edges
        for src, dst in self.edges:
            if src == curr:
                return dst
        
        return None


def normalize(state: dict) -> dict:
    # set defaults for missing fields
    defaults = {
        'batch_id': 'BATCH_001',
        'temperature': 0,
        'humidity': 0,
        'co2': 0,
        'light': 300,
        'product_type': 'Tomato',
        'location': 'Unknown',
        'text_report': '',
        'visual_report': '',
        'industrial_metrics': {
            'vibration': 0,
            'co2': 0,
            'delay_hours': 0
        }
    }
    
    for key, default_val in defaults.items():
        if key not in state:
            state[key] = default_val
    
    return state


def create_app(rag_instance=None) -> StateGraph:
    # build the analysis pipeline
    
    graph = StateGraph()
    
    # add nodes
    graph.add_node('normalize', normalize)
    graph.add_node('qualite', qualite_agent)
    graph.add_node('alertes', alertes_agent)
    graph.add_node('logistique', logistique_agent)
    graph.add_node('tracabilite', tracabilite_agent)
    
    # attach rag if provided
    if rag_instance:
        orig_q = graph.nodes['qualite']
        def qualite_with_rag(st):
            st['_rag_instance'] = rag_instance
            return orig_q(st)
        graph.add_node('qualite', qualite_with_rag)
    
    # direct edges
    graph.add_edge('normalize', 'qualite')
    graph.add_edge('logistique', 'tracabilite')
    
    # conditional routing after qualite
    def check_quality(st):
        if st.get('quality_status') == "BAD" or st.get('quality_score', 0) >= 0.45:
            return 'risky'
        return 'good'
    
    graph.add_conditional_edge('qualite', check_quality, {
        'risky': 'alertes',
        'good': 'logistique'
    })
    
    # alerts -> logistics
    graph.add_edge('alertes', 'logistique')
    
    graph.set_entry_point('normalize')
    
    return graph
