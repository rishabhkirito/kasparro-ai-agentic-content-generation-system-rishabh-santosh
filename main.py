import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from src.models import AgentState
from src.agents import (
    ingestion_node, 
    strategy_node, 
    qa_validation_node,
    comparison_logic_node, 
    assembly_node
)

load_dotenv()

# --- The "Brain" of the Loop ---
def should_retry(state: AgentState):
    """
    Decides whether to loop back to Strategy or move to Logic.
    Based on the output of the QA/Critic node.
    """
    if state.critique and state.retry_count < 3:
        # Loop back to Strategist
        return "retry"
    # Move forward to Logic Engine
    return "proceed"

# --- Build the Graph ---
workflow = StateGraph(AgentState)

# 1. Add Nodes
workflow.add_node("ingestion", ingestion_node)
workflow.add_node("strategist", strategy_node)
workflow.add_node("qa_validation", qa_validation_node)
workflow.add_node("logic_engine", comparison_logic_node)
workflow.add_node("assembly", assembly_node)

# 2. Define Edges (The Workflow)
workflow.set_entry_point("ingestion")
workflow.add_edge("ingestion", "strategist")
workflow.add_edge("strategist", "qa_validation")

# 3. The Agentic Loop (Conditional Edge)
workflow.add_conditional_edges(
    "qa_validation",
    should_retry,
    {
        "retry": "strategist",   # 🔄 LOOP: Go back to fix mistakes
        "proceed": "logic_engine" # ➡️ NEXT: Go to math/logic
    }
)

workflow.add_edge("logic_engine", "assembly")
workflow.add_edge("assembly", END)

app = workflow.compile()

# Input Data
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
    print("--- 🚀 Launching Kasparro AI Agent System (Phase 2 Architecture) ---")
    try:
        initial_state = AgentState(raw_input=INPUT_DATA)
        
        # Execute Graph with recursion limit (for loops)
        final_state = app.invoke(initial_state, config={"recursion_limit": 10})
        
        print("\n--- ✅ Workflow Complete ---")
        os.makedirs("output", exist_ok=True)
        
        with open("output/faq.json", "w") as f:
            f.write(final_state["faq_json"])
        with open("output/product_page.json", "w") as f:
            f.write(final_state["product_page_json"])
        with open("output/comparison_page.json", "w") as f:
            f.write(final_state["comparison_page_json"])
            
        print(f"Total FAQs: {len(final_state['questions'])}")
        print("Files saved to /output")

    except Exception as e:
        print(f"\n❌ System Error: {e}")

if __name__ == "__main__":
    main()