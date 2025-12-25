# src/agents/product_agent.py
import json
from src.models import Product
from src.blocks.text_utils import format_usage_instructions, generate_safety_warning
from src.blocks.math_utils import calculate_price_diff, compare_ingredients
from src.templates.schemas import ProductPageTemplate, ComparisonPageTemplate

class ProductPageAgent:
    """
    Responsibility: Assemble Product & Comparison Page JSONs.
    Satisfies Requirement: Assembler of pages using reusable blocks[cite: 37].
    """
    
    def build_product_page(self, p: Product) -> str:
        """
        Assembles the main Product Description Page.
        """
        # 1. Apply Reusable Logic Blocks (The "Muscles") [cite: 73]
        # These functions transform raw strings into structured lists/objects
        usage_block = format_usage_instructions(p.how_to_use)
        safety_block = generate_safety_warning(p.side_effects, p.skin_type)
        
        # 2. Render using Template (The "Skeleton") [cite: 79]
        # We pass only the data needed by the schema
        rendered_content = ProductPageTemplate.render(
            header_info={
                "name": p.name, 
                "price": p.price, 
                "currency": p.currency
            },
            details={
                "concentration": p.concentration,
                "key_benefits": p.benefits,
                "ingredients": p.ingredients
            },
            usage_block=usage_block,
            safety_block=safety_block
        )
        
        return json.dumps(rendered_content, indent=2)

    def build_comparison_page(self, p1: Product, p2: Product) -> str:
        """
        Assembles the Comparison Page (GlowBoost vs Competitor).
        """
        # 1. Apply Comparison Logic Blocks [cite: 78]
        # Calculates math (price diff) and set intersections (ingredients)
        price_analysis = calculate_price_diff(p1.price, p2.price)
        ingredient_analysis = compare_ingredients(p1.ingredients, p2.ingredients)
        
        # 2. Render using Template
        rendered_content = ComparisonPageTemplate.render(
            product_a_name=p1.name,
            product_b_name=p2.name,
            verdict=price_analysis['verdict'],
            tables={
                "price_comparison": {
                    "our_price": p1.price,
                    "competitor_price": p2.price,
                    "details": price_analysis
                },
                "ingredient_overlap": ingredient_analysis,
                "benefit_comparison": {
                    "us": p1.benefits,
                    "them": p2.benefits
                }
            }
        )
        
        return json.dumps(rendered_content, indent=2)