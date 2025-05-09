import tiktoken
from pathlib import Path

class TokenCounter:
    """Utility class for counting tokens in text"""
    
    def __init__(self, model="gpt-4o"):
        self.tokenizer = tiktoken.encoding_for_model(model)
        self.model = model
        
    def count_tokens(self, text):
        """Count the number of tokens in a text string"""
        return len(self.tokenizer.encode(text))
    
    def count_file_tokens(self, file_path):
        """Count tokens in a text file"""
        path = Path(file_path)
        if not path.exists():
            return 0
            
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
            return self.count_tokens(text)
    
    def estimate_cost(self, input_tokens, output_tokens=0):
        """Estimate cost based on current OpenAI pricing"""
        # Pricing as of May 2024 - update as needed
        if self.model == "gpt-4o":
            input_cost = input_tokens * 0.00001  # $0.01 per 1K tokens
            output_cost = output_tokens * 0.00003  # $0.03 per 1K tokens
            return input_cost + output_cost
        else:
            return 0  # Add pricing for other models as needed
    
    def print_token_summary(self, text, label="Text"):
        """Print a summary of token usage"""
        token_count = self.count_tokens(text)
        print(f"{label} contains {token_count} tokens")
        print(f"Estimated input cost: ${self.estimate_cost(token_count):.6f}")
        return token_count
