import json

class PaperAnalyzer:
    def __init__(self):
        self.schema = {
            "first_author": {"type": "string", "description": "First author's name"},
            "publication_date": {"type": "string", "description": "Date of publication"},
            "title": {"type": "string", "description": "Title of the paper"},
            "journal": {"type": "string", "description": "Name of the journal"},
            "external_training_data": {"type": "boolean", "description": "Whether external datasets were used for training"},
            "external_evaluation_data": {"type": "boolean", "description": "Whether external datasets were used for evaluation"},
            "small_dataset_techniques": {"type": "string", "description": "Techniques used to mitigate small dataset issues"},
            "data_heterogeneity": {"type": "string", "description": "Description of data heterogeneity and management methods"},
            "preprocessing": {"type": "string", "description": "Data preprocessing and noise handling steps"},
            "black_box_status": {"type": "boolean", "description": "Whether the model is considered a black box"},
            "evaluation_metrics": {"type": "string", "description": "Metrics used to evaluate model performance"},
            "species_breed": {"type": "string", "description": "Target species or breed, if applicable"},
            "ml_algorithm": {"type": "string", "description": "Machine learning algorithm or model type used"},
            "data_type": {"type": "string", "description": "Type of data used in the study"},
            "ai_goal": {"type": "string", "description": "Purpose of the AI system and target disease"},
            "clinical_implementation": {"type": "boolean", "description": "Whether the model has been implemented clinically or commercially"}
        }
    
    def analyze(self, text_chunks):
        """Analyze paper content and extract structured information"""
        # Handle both string and Document objects
        combined_text = "\n".join([
            chunk.page_content if hasattr(chunk, 'page_content') else str(chunk)
            for chunk in text_chunks
        ])
        
        # Create a simplified schema for the prompt
        simple_schema = {k: v["description"] for k, v in self.schema.items()}
        
        analysis_prompt = f"""
        You are a research paper analyzer. Extract specific information from this paper excerpt.
        Focus on finding factual information only. Do not make assumptions.
        If information is not explicitly stated, use "unknown".
        If a boolean field is unclear, default to false.

        Required format: Return a JSON object with these exact fields:
        {json.dumps(simple_schema)}

        Guidelines:
        - For authors: Look for the first author in the title page or header
        - For dates: Check the publication or submission date
        - For journal: Look for journal name in header or footer
        - For ML/AI fields: Focus on methodology and results sections
        - For boolean fields: Only mark true if explicitly stated

        Paper excerpt:
        {combined_text[:4000]}

        Return ONLY the JSON object, no other text.
        """
        
        try:
            # The LLM call will be handled by the agent, we just prepare the text
            return analysis_prompt
        except Exception as e:
            raise Exception(f"Error analyzing paper content: {str(e)}")
