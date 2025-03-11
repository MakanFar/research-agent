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
        You are an expert research paper analyzer specializing in AI/ML papers. Extract specific information from this paper excerpt.
        Be thorough and precise in your analysis. Search for both explicit and implicit information.

        Instructions:
        - Be thorough and precise in your analysis.
        - Look for information in all sections, including the title, headers, footers, citations, and body text.
        - If information is not found, return "unknown", but only after a thorough search.
        - For boolean fields, default to false only if the information is confidently not mentioned.

        Return a JSON object with the following fields:

        - First author:  
            type: string  
            description: First listed author (check title, header, author list).  
        - Publication date:  
            type: string  
            description: Extract from header, footer, or submission/acceptance dates.  
        - Journal:  
            type: string  
            description: Find in header, footer, or citation info.  
        - Title:  
            type: string  
            description: Extract full paper title.  
        - External training data:  
            type: boolean  
            description: True if external/public datasets were used for training.  
        - External validation data:  
            type: boolean  
            description: True if external/public datasets were used for validation.  
        - Small dataset:  
            type: boolean  
            description: True if small dataset limitations are mentioned.  
        - Small dataset techniques:  
            type: string  
            description: Note methods like upsampling, augmentation, or transfer learning.  
        - Data heterogeneity:  
            type: string  
            description: Mention variety in datasets, collection methods, or data types.  
        - Preprocessing:  
            type: string  
            description: List all data cleaning and preparation steps.  
        - ML algorithm:  
            type: string  
            description: Specify final models used (CNN, RNN, etc.).  
        - Data type:  
            type: string  
            description: Describe data used (images, text, clinical data, etc.).  
        - AI goal:  
            type: string  
            description: State the medical/clinical objective.  
        - Evaluation metrics:  
            type: string  
            description: List metrics (accuracy, F1, sensitivity, specificity, etc.).  
        - Performance results:  
            type: string  
            description: Summarize key performance outcomes.  
        - Black box status:  
            type: boolean  
            description: True if no XAI techniques (e.g., feature importance, Grad-CAM) are mentioned.  
        - Model Interpretability:  
            type: string  
            description: List XAI methods used (Grad-CAM, LRP, feature importance) or set as None if absent.  
        - Clinical implementation:  
            type: boolean  
            description: True if real-world deployment is mentioned.  
        - Species/breed:  
            type: string  
            description: Specify animal types studied.  


        Example output:
         {{
            "first_author": "Aurora Rosvoll Groendahl",
            "publication_date": "March 2023",
            "journal": "Frontiers in Veterinary Science",
            "title": "Automatic gross tumor segmentation of canine head and neck cancer using deep learning and cross-species transfer learning",
            "external_training_data": True,
            "external_validation_data": False,
            "small_dataset": True,
            "small_dataset_techniques": "cross-species transfer learning",
            "data_heterogeneity": "Data from both human and canine datasets were used, with inherent differences in anatomy and disease characteristics between species.",
            "preprocessing": "Images were cropped and/or padded to standardize dimensions, Gaussian noise was added",
            "ml_algorithm": "3D U-Net architecture",
            "data_type": "Contrast-enhanced computed tomography (CT) images",
            "ai_goal": "To evaluate the applicability of deep learning-based automatic segmentation of the gross tumor volume (GTV) in canine patients with head and neck cancer.",
            "evaluation_metrics": "Dice similarity coefficient, true positive rate (TPR), positive predictive value (PPV), Hausdorff distance (HD95)",
            "performance_results": "Transfer learning model achieved a maximum Dice of 0.89 and a minimum ASD of 1.3 mm. Canine-only model showed higher tumor coverage but included more normal tissue.",
            "black_box_status": False,
            "Interpretability techniques": "Grad-cam",
            "clinical_implementation": False
            "species_breed": "canine",

        }}

        Paper excerpt:
        {combined_text[:25000]}
        """
        
        
        try:
            # The LLM call will be handled by the agent, we just prepare the text
            return analysis_prompt
        except Exception as e:
            raise Exception(f"Error analyzing paper content: {str(e)}")
