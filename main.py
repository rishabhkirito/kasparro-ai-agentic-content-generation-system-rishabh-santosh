# main.py
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from src.models import AgentState
from src.agents import ingestion_node, strategy_node, comparison_logic_node, assembly_node

# 1. Load Environment Variables
load_dotenv()

# 2. Build the Graph
workflow = StateGraph(AgentState)

# 3. Add Nodes (The Agents)
workflow.add_node("ingestion", ingestion_node)
workflow.add_node("strategist", strategy_node)
workflow.add_node("logic_engine", comparison_logic_node)
workflow.add_node("assembly", assembly_node)

# 4. Define Edges (The Automation Flow)
workflow.set_entry_point("ingestion")
workflow.add_edge("ingestion", "strategist")
workflow.add_edge("strategist", "logic_engine")
workflow.add_edge("logic_engine", "assembly")
workflow.add_edge("assembly", END)

# 5. Compile
app = workflow.compile()

# 6. Run
INPUT_DATA = """
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
    print("--- 🚀 Launching Kasparro AI Agent System (LangGraph + Gemini) ---")
    
    try:
        initial_state = AgentState(raw_input=INPUT_DATA)

        print(app.get_graph().draw_ascii())
        
        # Execute the Graph
        final_state = app.invoke(initial_state)
        
        print("\n--- ✅ Workflow Complete ---")
        
        # Output to files
        os.makedirs("output", exist_ok=True)
        with open("output/product_page.json", "w") as f:
            f.write(final_state["product_page_json"])
        with open("output/faq.json", "w") as f:
            f.write(final_state["faq_json"])
        with open("output/comparison_page.json", "w") as f:
            f.write(final_state["comparison_page_json"])
            
        print(f"Competitor Created by AI: {final_state['competitor'].name}")
        print("Files saved to /output")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Tip: Check if your .env file exists and contains GOOGLE_API_KEY.")

if __name__ == "__main__":
    main()