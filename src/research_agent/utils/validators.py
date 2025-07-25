from pydantic import  BaseModel, Field, create_model
from typing import Literal
from ..config.config import config
import os

config = config.load_config("config.yaml")


class FilterModel(BaseModel):
    relevant: bool = Field(description="Choose whether the article is relevant and meets the criteria. Must be True or False in boolean")
    reason: str = Field(description="short explanation why the abstract matches or not")
    confidence: Literal["Low","Medium","High"] = Field(description="Select your level of confidence in the relevance assessment. Must be one of: 'Low', 'Medium', or 'High'.")

def metaAnalysisModel() -> type:
    
    meta_data_fields = {k: v for d in config["meta_data"] for k, v in d.items()}

    return create_model(
        "MetaAnalysisModel",
        **{
        k: (str, Field(..., description=v))
        for k, v in meta_data_fields.items()
        }
    )

def bodyAnalysisModel() -> type:

    body_data_fields = {k: v for d in config["in_depth"] for k, v in d.items()}
    
    return create_model(
        "BodyAnalysisModel",
        **{
        k: (str, Field(..., description=v))
        for k, v in body_data_fields.items()
        }
    )


def SystematicReviewModel() -> type:
    
    return create_model(
        "SystematicReviewModel",
        meta_data=(metaAnalysisModel(), ...),
        body_data=(bodyAnalysisModel(), ...)
    )
