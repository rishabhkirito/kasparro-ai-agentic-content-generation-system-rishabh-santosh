# src/agents.py
import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.models import AgentState, Product, Competitor, Question, ComparisonData
from src.logic_tools import calculate_price_delta, extract_ingredient_overlap

# 1. Load Environment Variables
load_dotenv()

# 2. Initialize Gemini (It will automatically find GOOGLE_API_KEY in env)
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found in .env file")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2)

# --- Node 1: Ingestion Agent ---
def ingestion_node(state: AgentState) -> dict:
    print("🤖 [Ingestion Agent] Parsing raw text with Gemini...")
    
    parser = PydanticOutputParser(pydantic_object=Product)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a data extraction specialist. Extract the product details into strict JSON. If data is missing, infer logically or use 'None'."),
        ("user", "Raw Text: {raw_text}\n\n{format_instructions}")
    ])
    
    chain = prompt | llm | parser
    try:
        product_data = chain.invoke({
            "raw_text": state.raw_input, 
            "format_instructions": parser.get_format_instructions()
        })
        return {"product": product_data}
    except Exception as e:
        print(f"Error in ingestion: {e}")
        return {}

# --- Node 2: Strategist Agent (Creative) ---
def strategy_node(state: AgentState) -> dict:
    print("🧠 [Strategist Agent] Inventing competitor & brainstorming questions...")
    p = state.product
    
    # A. Generate Competitor
    comp_parser = PydanticOutputParser(pydantic_object=Competitor)
    comp_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a fierce marketing strategist. Analyze the target product. Create a FICTIONAL competitor that challenges it directly (either cheaper with worse ingredients, or premium with better ones)."),
        ("user", "Target Product: {p_name} ({p_price}). Ingredients: {p_ing}. \n\nGenerate Competitor JSON:\n{format_instructions}")
    ])
    competitor = (comp_prompt | llm | comp_parser).invoke({
        "p_name": p.name, "p_price": p.price, "p_ing": p.ingredients,
        "format_instructions": comp_parser.get_format_instructions()
    })

    # B. Generate Questions
    # We ask for a LIST of questions
    q_prompt = ChatPromptTemplate.from_messages([
        ("system", "Generate 5 critical user questions (Safety, Usage, Value) based on the product data."),
        ("user", "Product: {p_name}, Side Effects: {p_side_effects}, Price: {p_price}. Return a JSON list of objects with keys: category, question, answer.")
    ])
    q_response = llm.invoke(q_prompt.format(p_name=p.name, p_side_effects=p.side_effects, p_price=p.price))
    
    # Helper to parse the generic list
    try:
        raw_content = q_response.content.replace("```json", "").replace("```", "")
        q_data = json.loads(raw_content)
        questions = [Question(**q) for q in q_data]
    except:
        questions = []

    return {"competitor": competitor, "questions": questions}

# --- Node 3: Content Logic Agent (The "Block" user) ---
def comparison_logic_node(state: AgentState) -> dict:
    print("⚖️ [Content Logic] Running math & set operations...")
    p = state.product
    c = state.competitor
    
    # 1. Deterministic Math Logic (The "Block")
    price_stats = calculate_price_delta(p.price, c.price)
    ing_stats = extract_ingredient_overlap(p.ingredients, c.ingredients)
    
    # 2. AI Synthesis of the Logic
    verdict = "Better Value" if price_stats['is_cheaper'] else "Premium Choice"
    adv_summary = f"We have {len(ing_stats['unique_to_p1'])} unique ingredients."
    
    analysis = ComparisonData(
        verdict=verdict,
        price_diff=price_stats['diff'],
        advantage_summary=adv_summary,
        common_ingredients=ing_stats['common']
    )
    
    return {"comparison_analysis": analysis}

# --- Node 4: Assembly Agent (Output Generation) ---
def assembly_node(state: AgentState) -> dict:
    print("📝 [Assembly Agent] Formatting final JSON files...")
    
    # We construct the final JSONs based on the Accumulated State
    # 1. Product Page
    prod_json = state.product.model_dump_json(indent=2)
    
    # 2. FAQ Page
    faq_data = {
        "title": "FAQ",
        "items": [q.model_dump() for q in state.questions]
    }
    faq_json = json.dumps(faq_data, indent=2)
    
    # 3. Comparison Page
    comp_json = json.dumps({
        "product_a": state.product.name,
        "product_b": state.competitor.name,
        "analysis": state.comparison_analysis.model_dump()
    }, indent=2)
    
    return {
        "product_page_json": prod_json,
        "faq_json": faq_json,
        "comparison_page_json": comp_json
    }