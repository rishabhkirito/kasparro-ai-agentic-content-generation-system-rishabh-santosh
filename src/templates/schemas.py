# src/templates/schemas.py
from typing import List, Dict, Any

class BaseTemplate:
    """Base class for all templates to ensure consistent metadata."""
    @staticmethod
    def _add_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "meta": {
                "generated_by": "Kasparro Auto-Agent",
                "version": "1.0",
                "content_type": "application/json"
            },
            "data": data
        }

class FAQTemplate(BaseTemplate):
    """
    Template for the FAQ Page.
    Defines the structure for categorized questions.
    """
    @classmethod
    def render(cls, categories: Dict[str, List[Dict[str, str]]]) -> Dict[str, Any]:
        content = {
            "page_title": "Frequently Asked Questions",
            "description": "Common questions regarding usage, safety, and results.",
            "sections": []
        }
        
        # Convert dictionary to ordered list of sections for cleaner JSON
        for category_name, qa_list in categories.items():
            content["sections"].append({
                "category": category_name,
                "q_and_a_list": qa_list
            })
            
        return cls._add_metadata(content)

class ProductPageTemplate(BaseTemplate):
    """
    Template for the Main Product Landing Page.
    """
    @classmethod
    def render(cls, 
               header_info: Dict[str, Any], 
               details: Dict[str, Any], 
               usage_block: Dict[str, Any], 
               safety_block: Dict[str, Any]) -> Dict[str, Any]:
        
        content = {
            "hero_section": {
                "product_title": header_info.get("name"),
                "price_display": f"{header_info.get('currency')} {header_info.get('price')}",
                "availability": "In Stock"
            },
            "product_details": details,
            "instruction_manual": usage_block,
            "safety_information": safety_block
        }
        
        return cls._add_metadata(content)

class ComparisonPageTemplate(BaseTemplate):
    """
    Template for the Competitor Comparison Page.
    """
    @classmethod
    def render(cls, 
               product_a_name: str, 
               product_b_name: str, 
               verdict: str, 
               tables: Dict[str, Any]) -> Dict[str, Any]:
        
        content = {
            "page_header": f"{product_a_name} vs. {product_b_name}",
            "buying_guide_verdict": verdict,
            "comparison_tables": tables,
            "disclaimer": "Competitor data is simulated for demonstration purposes."
        }
        
        return cls._add_metadata(content)