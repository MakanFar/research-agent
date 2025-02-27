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
        combined_text = "\n".join([chunk.page_content for chunk in text_chunks])
        
        analysis_prompt = f"""
        Analyze the following academic paper text and extract the requested information.
        Return the information in a JSON format matching exactly these fields:
        {json.dumps(self.schema, indent=2)}
        
        Paper text:
        {combined_text}
        """
        
        try:
            # The LLM call will be handled by the agent, we just prepare the text
            return analysis_prompt
        except Exception as e:
            raise Exception(f"Error analyzing paper content: {str(e)}")
