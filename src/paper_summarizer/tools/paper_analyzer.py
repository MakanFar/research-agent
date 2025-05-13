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
            "performance_results": {"type": "string", "description": "Performance results of models, including accuracy, precision, recall, F1-score, AUC, etc."},
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
        
        
        analysis_prompt = f"""
        You are an expert at analyzing academic papers. Extract key information accurately. Be thorough and precise in your analysis. Search for both explicit and implicit information and follow the instructions.

        Instructions:
        - Don't add any knowledge from yourself, and don't make assumptions. Only rely on the information provided in the paper
        - Be thorough and precise in your analysis.
        - Write the results concise 
        - Look for information in all sections.
        - If information is not found in the paper, return "unknown", but only after a thorough search.
        - For boolean fields, default to False only if the information is confidently not mentioned.

        Extract key information from this paper excerpt. Return a JSON object with these fields:
        - first_author: First listed author's name on paper
        - publication_date: Year that paper was published
        - title: Paper title
        - data_type: Type of data used in the study such as radiology, clinicopathologic, or text
        - species_breed: Target species
        - ml_algorithm: Types Model used in the study
        - ai_goal: Clinical objective of the study
        - clinical_implementation: Boolean. Set true if study was actually deployed and adopted in real life.
        - external_training_data: Boolean. Set True if external datasets such as data from multiple sources are used
        - external_validation_data: Boolean. Set to True if the model has been evaluated using external datasets or data from other sources. 
        - small_dataset: Boolean. Set to True if the paper mentions lack of data OR if the data used to train the model is less than 1000 samples
        - small_dataset_techniques: In cases of limited data, mention methods that authors use to mitigate the issue—such as transfer learning, data augmentation, and similar techniques.
        - data_heterogeneity: Mention of the authors use heterogeneous data or attempt to add variability through different types of data, data from various sources, different collection processes, or any other methods that could increase heterogeneity.
        - preprocessing: Data preprocessing techniques used to to handel the noise, or missing data, or class imbalance
        - regularization: regularization techniques used to stop model from overfiting such as early stopping, dropout or l1 and l2 regularization
        - black_box_status: Boolean. Set to True if the model lacked explainability methods such as feature importance, Grad-CAM, or other means of providing interpretability.
        - evaluation_metrics: Performance metrics used for evaluting the model
        - performance_results: Key final results
        - ethics: Ethical implications discussed by the authors
        
        Return concise JSON only, no explanations.
        Paper excerpt:
        {combined_text[:25000]}
        """
        
        
        try:
            # The LLM call will be handled by the agent, we just prepare the text
            return analysis_prompt
        except Exception as e:
            raise Exception(f"Error analyzing paper content: {str(e)}")
