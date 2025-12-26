# src/models.py
from typing import List, Optional
from pydantic import BaseModel, Field

# --- 1. Product Models ---
class Product(BaseModel):
    """Internal model for the main product."""
    name: str = Field(description="Name of the product")
    price: float = Field(description="Numeric price value")
    currency: str = Field(description="Currency code like INR, USD")
    concentration: Optional[str] = Field(None, description="Active ingredient concentration")
    skin_type: List[str] = Field(description="List of suitable skin types")
    ingredients: List[str] = Field(description="List of key ingredients")
    benefits: List[str] = Field(description="List of product benefits")
    how_to_use: str = Field(description="Usage instructions")
    side_effects: Optional[str] = Field(None, description="Side effects or warnings")

class Competitor(Product):
    """Model for the AI-generated competitor."""
    reason_for_creation: str = Field(description="Why this competitor was created (e.g. 'Cheaper alternative')")

# --- 2. Content Models ---
class Question(BaseModel):
    category: str = Field(description="Category like Safety, Usage, etc.")
    question: str
    answer: str

class ComparisonData(BaseModel):
    verdict: str
    price_diff: float
    advantage_summary: str
    common_ingredients: List[str]

# --- 3. The State (The Shared Memory of the Graph) ---
class AgentState(BaseModel):
    """The shared state passed between agents in the graph."""
    raw_input: str
    product: Optional[Product] = None
    competitor: Optional[Competitor] = None
    questions: List[Question] = []
    comparison_analysis: Optional[ComparisonData] = None
    
    # Final JSON Outputs
    faq_json: str = ""
    product_page_json: str = ""
    comparison_page_json: str = ""