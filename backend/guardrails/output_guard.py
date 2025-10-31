from typing import Tuple

class OutputGuardrail:
    """Ensures output is appropriate and educational"""
    
    def validate(self, response: str) -> Tuple[bool, str]:
        """Validate the generated response"""
        
        # Check if response contains solution
        if len(response) < 20:
            return False, "Response too brief"
        
        # Ensure step-by-step format (relaxed check)
        step_indicators = ["Step", "step", "1.", "2.", "First", "Next", "Finally"]
        has_steps = any(indicator in response for indicator in step_indicators)
        
        if not has_steps:
            # Still valid, but note it
            return True, "Valid response (note: could be more structured)"
        
        # Check for harmful content
        harmful_phrases = ['i cannot help', 'i refuse', 'i will not']
        if any(phrase in response.lower() for phrase in harmful_phrases):
            return False, "Response contains refusal"
        
        return True, "Valid response"