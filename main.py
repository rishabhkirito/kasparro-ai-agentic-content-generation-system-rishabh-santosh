# main.py
import os
from src.agents.ingestion_agent import DataIngestionAgent
from src.agents.strategist_agent import StrategistAgent
from src.agents.faq_agent import FAQAgent
from src.agents.product_agent import ProductPageAgent

# Raw Input Data (Source: [cite: 13-22])
RAW_DATA = """
Product Name: GlowBoost Vitamin C Serum
Concentration: 10% Vitamin C
Skin Type: Oily, Combination
Key Ingredients: Vitamin C, Hyaluronic Acid
Benefits: Brightening, Fades dark spots
How to Use: Apply 2-3 drops in the morning before sunscreen
Side Effects: Mild tingling for sensitive skin
• Price: ₹699
"""

def main():
    print("--- Starting Kasparro Multi-Agent System ---")
    
    # 1. Ingestion Agent: Parse Data
    print("[Agent 1] Ingestion Agent: Parsing raw data...")
    ingestor = DataIngestionAgent()
    product_model = ingestor.parse(RAW_DATA)
    print(f"   -> Model Created: {product_model.name} ({product_model.price})")

    # 2. Strategist Agent: Generate Strategy & Competitor
    print("[Agent 2] Strategist Agent: Generating synthetic content...")
    strategist = StrategistAgent()
    questions = strategist.generate_questions(product_model)
    competitor = strategist.generate_competitor()
    print(f"   -> Generated {len(questions)} questions.")
    print(f"   -> Generated Competitor: {competitor.name}")

    # 3. Execution Agents: Build Pages
    print("[Agent 3] Building Content Pages...")
    
    # Build FAQ
    faq_agent = FAQAgent()
    faq_json = faq_agent.build(questions)
    
    # Build Product & Comparison
    prod_agent = ProductPageAgent()
    product_json = prod_agent.build_product_page(product_model)
    comp_json = prod_agent.build_comparison_page(product_model, competitor)

    # 4. Output Generation
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f"{output_dir}/faq.json", "w") as f:
        f.write(faq_json)
    
    with open(f"{output_dir}/product_page.json", "w") as f:
        f.write(product_json)
        
    with open(f"{output_dir}/comparison_page.json", "w") as f:
        f.write(comp_json)

    print(f"--- Success! Check the '{output_dir}' folder for JSON files. ---")

if __name__ == "__main__":
    main()