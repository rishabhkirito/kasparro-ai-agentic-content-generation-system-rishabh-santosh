# src/models.py
from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class Product:
    """
    Internal model representing a product.
    Source: [cite: 13, 14, 15]
    """
    name: str
    price: float
    currency: str
    concentration: Optional[str] = None
    skin_type: List[str] = field(default_factory=list)
    ingredients: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    how_to_use: str = ""
    side_effects: Optional[str] = None

@dataclass
class Question:
    """
    Represents a generated user question.
    Source: [cite: 28, 29]
    """
    category: str  # e.g., Safety, Usage, Purchase
    question_text: str
    answer_text: str  # The answer derived from product data