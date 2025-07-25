from .base import BaseConfig

DEFAULT_CONFIG: BaseConfig = {
    "papers_directory": "./papers",
    "output_directory": "./output",
    "OPENAI_API_KEY": None,
    "NCBI_API_KEY": None,
    "search_query":None,
    "meta_data": {
        "data_type": "Type of data used in the study such as radiology, clinicopathologic, or text",
        "species_breed": "Target species",
        "ml_algorithm": "Types Model used in the study",
        "ai_goal": "Clinical objective of the study",
        "performance_results": "Key final performance results"
    },  
    "in_depth": {
        "small_dataset": "Short explanation if fewer than ~1000 samples OR authors mention limited data. Infer from methods if possible, else return unknown.",
    }
}