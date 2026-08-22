"""Cognitive Taxonomy and Pydantic validation schemas for Myntra Wishlist Discovery."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CognitiveCategory(str, Enum):
    """Rigid 5-category taxonomy including 4 non-monetary friction categories and 1 excluded monetary category."""
    STYLING_ISOLATION = "Styling_Isolation"
    FIT_BODY_AMBIGUITY = "Fit_Body_Ambiguity"
    OCCASION_DISCONNECT = "Occasion_Disconnect"
    CATALOG_CLUTTER = "Catalog_Clutter"
    MONETARY_WAIT = "Monetary_Wait"  # Flagged and purged by Zero-Monetary rule


class ClassificationResult(BaseModel):
    """Strict structured output model for LLM classification."""
    primary_category: CognitiveCategory = Field(
        ...,
        description="The primary cognitive hesitation category identified from the customer feedback."
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score of the classification between 0.0 and 1.0."
    )
    verbatim_quote: str = Field(
        ...,
        description="Exact substring extracted directly from the customer text proving the hesitation rationale."
    )
    decision_barrier_summary: str = Field(
        ...,
        description="One-sentence executive synthesis of the specific barrier preventing checkout."
    )
    secondary_category: Optional[CognitiveCategory] = Field(
        default=None,
        description="Optional secondary category if multiple friction points are present."
    )

    @field_validator("confidence_score")
    @classmethod
    def round_confidence(cls, v: float) -> float:
        return round(float(v), 4)
