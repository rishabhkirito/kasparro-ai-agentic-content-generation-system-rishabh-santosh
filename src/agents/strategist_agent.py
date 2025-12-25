# src/agents/strategist_agent.py
from src.models import Product, Question
import random # Optional, added if you want slight variety in future

class StrategistAgent:
    """
    Responsibility: Generate synthetic content (Questions & Competitor).
    Satisfies Requirement: 
    - [cite_start]Automatically generate at least 15 categorized user questions [cite: 28]
    - [cite_start]Create structured fictional competitor [cite: 42]
    """
    
    def generate_competitor(self) -> Product:
        """
        Creates a fictional 'Product B' for comparison.
        [cite_start]The assignment requires this to be structured (name, ingredients, benefits, price)[cite: 42].
        """
        return Product(
            name="DermaGlow Generic Serum",
            price=899.0,
            currency="INR",
            concentration="5% Vitamin C",
            skin_type=["All Skin Types"],
            ingredients=["Vitamin C", "Water", "Glycerin", "Phenoxyethanol"],
            benefits=["Basic Hydration", "Mild Brightening"],
            how_to_use="Apply daily.",
            side_effects="None reported"
        )

    def generate_questions(self, p: Product) -> list[Question]:
        """
        [cite_start]Generates 15+ categorized questions using slot-filling templates[cite: 28, 30].
        Includes conditional logic for Price and Safety tone.
        """
        questions = []
        
        # --- 1. Informational Category ---
        # Logic: Extract facts to answer general queries
        questions.append(Question("Informational", f"What is the main benefit of {p.name}?", f"The main benefits are {', '.join(p.benefits)}."))
        questions.append(Question("Informational", f"What is the concentration of active ingredients?", f"It contains {p.concentration or 'standard concentration'}."))
        questions.append(Question("Informational", f"What are the key ingredients?", f"It features {', '.join(p.ingredients)}."))
        questions.append(Question("Informational", "Is this a serum or a cream?", "This is a serum formulation."))
        questions.append(Question("Informational", "Can I use this for dull skin?", "Yes, it is designed for: " + ", ".join(p.benefits)))
        
        # --- 2. Usage Category ---
        # Logic: Use the 'how_to_use' field directly
        questions.append(Question("Usage", "How do I apply this product?", p.how_to_use))
        questions.append(Question("Usage", "Can I use this in the morning?", "Yes, " + p.how_to_use))
        questions.append(Question("Usage", "How many drops should I use?", "Please apply 2-3 drops as directed."))
        questions.append(Question("Usage", "Do I need sunscreen after using this?", "Yes, it is recommended to apply before sunscreen."))
        questions.append(Question("Usage", "Can I layer this with other products?", "Always apply thinnest to thickest. This serum goes first."))

        # --- 3. Safety Category ---
        # Logic: Check for 'sensitive' warnings or side effects to determine tone
        safe_for_sensitive = "Yes"
        if p.side_effects and ("tingling" in p.side_effects.lower() or "redness" in p.side_effects.lower() or "not safe" in p.side_effects.lower()):
            safe_for_sensitive = f"Please note: {p.side_effects}"
        
        questions.append(Question("Safety", "Are there any side effects?", p.side_effects or "No major side effects listed."))
        questions.append(Question("Safety", "Is this safe for sensitive skin?", safe_for_sensitive))
        questions.append(Question("Safety", "Will this cause tingling?", f"You may experience {p.side_effects.lower()}" if p.side_effects else "Likely not."))
        
        # Logic: Check compatible skin types
        target_skin = p.skin_type[0] if p.skin_type else "your skin type"
        questions.append(Question("Safety", f"Is {p.name} suitable for {target_skin} skin?", "Yes, it is formulated for this skin type."))
        questions.append(Question("Safety", "Is it non-comedogenic?", "It is formulated for " + ", ".join(p.skin_type)))

        # --- 4. Purchase/Value Category ---
        # Logic: Smart Price Adjective based on value [New Logic]
        # If price < 1000 -> "competitively priced", else -> "premium formulation"
        price_adjective = "competitively priced" if p.price < 1000 else "a premium formulation"
        
        questions.append(Question("Purchase", "What is the price?", f"{p.currency} {p.price}"))
        questions.append(Question(
            "Purchase", 
            "Is this affordable?", 
            f"At {p.currency} {p.price}, it is {price_adjective} containing {p.concentration or 'active ingredients'}."
        ))
        
        # --- 5. Comparison Category ---
        questions.append(Question("Comparison", "Why choose this over others?", f"It offers {p.concentration} and {p.ingredients[0] if p.ingredients else 'quality ingredients'} for enhanced results."))

        return questions