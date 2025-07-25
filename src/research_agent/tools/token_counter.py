
import tiktoken

class TokenManager:

    def __init__(self, model_name, max_tokens=35000):
     
        # Initialize tokenizer for accurate token counting
        self.tokenizer = tiktoken.encoding_for_model(model_name)
        self.max_tokens = max_tokens

    def count_tokens(self, text):
        """Count tokens in text using the model's tokenizer"""
        return self.tokenizer.encode(text)

    def estimate_prompt_tokens(self, system_prompt, user_input):
        """Estimate total tokens for a prompt"""
        system_tokens = self._count_tokens(system_prompt)
        user_tokens = self._count_tokens(user_input)
        # Add buffer for message formatting and response
        total_tokens = len(system_tokens) + len(user_tokens) + 3000  # Buffer for response
        return total_tokens

    def truncate_content(self, content, max_tokens):
        """Truncate content to fit within token limits"""
        content_tokens = self._count_tokens(content)
        if len(content_tokens) <= max_tokens:
            return content

        # Truncate tokens precisely
        truncated_tokens = content_tokens[:max_tokens]
        truncated_text = self.tokenizer.decode(truncated_tokens)

        # Try to end at sentence boundary if possible
        last_period = truncated_text.rfind('.')
        if last_period > len(truncated_text) * 0.8:
            truncated_text = truncated_text[:last_period + 1]

        return truncated_text + "\n\n[Truncated to fit token limit]"
    
    def check_token_limit(self, prompt, processed_article):
        # Double-check token count before processing
        system_prompt = self.prompt.messages[0].prompt.template
        if hasattr(self, 'meta_data'):
            system_prompt = system_prompt.format(self.meta_data)

        estimated_tokens = self._estimate_prompt_tokens(system_prompt, processed_article)
        print("estimated_tokens: ", estimated_tokens)

        if estimated_tokens > self.max_tokens:
            # Emergency truncation
            max_content_tokens = self.max_tokens - len(self._count_tokens(system_prompt))
            processed_article = self._truncate_content(processed_article, max_content_tokens)
         
        return processed_article




