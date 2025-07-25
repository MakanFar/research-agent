from typing import Union, List, Dict, Any
from typing_extensions import TypedDict


class BaseConfig(TypedDict):
    papers_directory: str
    output_directory: str
    OPENAI_API_KEY: str
    NCBI_API_KEY: str
    meta_data: Dict
    in_depth: Dict
