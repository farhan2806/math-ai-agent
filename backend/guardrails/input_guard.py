import re
from typing import Tuple

class InputGuardrail:
    """Ensures only math-related queries are processed"""
    
    MATH_KEYWORDS = [
        'solve', 'derivative', 'integral', 'equation', 'calculate',
        'find', 'prove', 'simplify', 'factor', 'graph', 'matrix',
        'vector', 'trigonometry', 'algebra', 'calculus', 'geometry',
        'probability', 'statistics', 'theorem', 'formula', 'evaluate'
    ]
    
    BLOCKED_TOPICS = [
        'politics', 'religion', 'violence', 'adult', 'illegal',
        'personal information', 'password', 'hack', 'exploit',"porn"
    ]
    
    def validate(self, query: str) -> Tuple[bool, str]:
        """
        Returns: (is_valid, message)
        """
        query_lower = query.lower()
        
        # Check length
        if len(query) < 5:
            return False, "Query too short. Please ask a complete math question."
        
        if len(query) > 500:
            return False, "Query too long. Please keep it under 500 characters."
        
        # Check for blocked content
        for blocked in self.BLOCKED_TOPICS:
            if blocked in query_lower:
                return False, "This system only handles mathematics questions."
        
        # Check if it contains math-related terms
        has_math_term = any(keyword in query_lower for keyword in self.MATH_KEYWORDS)
        
        # Check for mathematical symbols/numbers
        has_math_symbols = bool(re.search(r'[\d+\-*/=^∫∑√π]', query))
        
        if not (has_math_term or has_math_symbols):
            return False, "Please ask a mathematics-related question."
        
        return True, "Valid math query"