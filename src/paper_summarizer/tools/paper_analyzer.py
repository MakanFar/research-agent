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
        You are an expert research paper analyzer specializing in AI/ML papers. Extract specific information from this paper excerpt.
        Be thorough and precise in your analysis. Search for both explicit and implicit information.

        Required format: Return a JSON object with these exact fields:
        {json.dumps(simple_schema)}

        Detailed Guidelines:
        1. Paper Metadata:
           - First author: Look in title, header, author list (take first listed)
           - Publication date: Check header, footer, submission/acceptance dates
           - Journal: Search header, footer, citation info
           - Title: Extract complete paper title
        
        2. Data & Methodology:
           - External data: Mark true if mentions external datasets, databases, or public data
           - Small dataset techniques: Look for data augmentation, transfer learning, etc.
           - Data heterogeneity: Note any mentions of data variety, using different datasets or handling different data types
           - Preprocessing: List all data cleaning, normalization, or preparation steps
        
        3. ML/AI Specifics:
           - ML algorithm: Include final models used  (CNN, RNN, etc.)
           - Data type: Specify data types used for training the model (images, text, clinical data, etc.)
           - AI goal: Describe the specific medical/clinical objective
           - Evaluation metrics: List all metrics (accuracy, precision, F1, etc.)
        
        4. Implementation:
           - Black box status: Mark true if model interpretability is not discussed
           - Clinical implementation: Mark true if mentions real-world deployment
        
        5. Species/Medical:
           - Species/breed: Note animal types mentioned for the study

        If information is truly not found after thorough search, use "unknown".
        For boolean fields, default to false only if confidently not mentioned.

        Paper excerpt:
        {combined_text[:4000]}

        Return ONLY a valid JSON object, no additional text.
        Ensure all field names exactly match the schema.
        """
        
        
        try:
            # The LLM call will be handled by the agent, we just prepare the text
            return analysis_prompt
        except Exception as e:
            raise Exception(f"Error analyzing paper content: {str(e)}")
