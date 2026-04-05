"""
Simple RAG - stores and retrieves similar cases using Jaccard similarity
"""


class SimpleRAG:
    def __init__(self):
        self.memory_texts = []
        self.memory_token_sets = []
    
    def _tokenize(self, txt: str) -> set:
        # convert to lowercase tokens
        if not txt:
            return set()
        import re
        tokens = re.findall(r'\w+', txt.lower())
        return set(tokens)
    
    def store(self, state: dict):
        # store case in memory
        txt = (
            f"temp {state.get('temperature', 0)} "
            f"humidity {state.get('humidity', 0)} "
            f"co2 {state.get('co2', 0)} "
            f"light {state.get('light', 0)} "
            f"fruit {state.get('product_type', '')} "
            f"status {state.get('quality_status', '')} "
            f"text {state.get('text_report', '')} "
            f"visual {state.get('visual_report', '')}"
        )
        
        tokens = self._tokenize(txt)
        self.memory_texts.append(txt)
        self.memory_token_sets.append(tokens)
    
    def retrieve_similar(self, state: dict, k: int = 3) -> list:
        # find k most similar cases using jaccard
        if not self.memory_texts:
            return []
        
        query = (
            f"temp {state.get('temperature', 0)} "
            f"humidity {state.get('humidity', 0)}"
        )
        q_tokens = self._tokenize(query)
        
        # calc similarity for each
        scores = []
        for i, mem_tok in enumerate(self.memory_token_sets):
            if not q_tokens and not mem_tok:
                jac = 1.0
            elif not q_tokens or not mem_tok:
                jac = 0.0
            else:
                inter = len(q_tokens & mem_tok)
                union = len(q_tokens | mem_tok)
                jac = inter / union if union > 0 else 0.0
            
            if jac > 0:
                scores.append((jac, self.memory_texts[i]))
        
        scores.sort(key=lambda x: x[0], reverse=True)
        return [txt for _, txt in scores[:k]]
