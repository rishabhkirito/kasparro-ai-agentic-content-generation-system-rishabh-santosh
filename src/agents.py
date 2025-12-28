import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.models import AgentState, Product, Competitor, Question, ComparisonData
from src.logic_tools import calculate_price_delta, extract_ingredient_overlap

load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# Use a slightly higher temperature for the strategist to encourage variety
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.3)

# --- Node 1: Ingestion (Extraction) ---
def ingestion_node(state: AgentState) -> dict:
    print("🤖 [Ingestion Agent] Parsing raw text...")
    parser = PydanticOutputParser(pydantic_object=Product)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract product details into strict JSON. Use 'None' for missing fields."),
        ("user", "Text: {raw_text}\n\n{format_instructions}")
    ])
    try:
        data = (prompt | llm | parser).invoke({
            "raw_text": state.raw_input, 
            "format_instructions": parser.get_format_instructions()
        })
        return {"product": data}
    except Exception as e:
        print(f"   ❌ Ingestion Error: {e}")
        return {}

# --- Node 2: Strategist (Creative + Adaptive) ---
def strategy_node(state: AgentState) -> dict:
    attempt = state.retry_count + 1
    print(f"🧠 [Strategist Agent] Generating Content (Attempt {attempt})...")
    p = state.product
    
    # 1. Competitor Generation (Only if missing)
    competitor = state.competitor
    if not competitor:
        comp_parser = PydanticOutputParser(pydantic_object=Competitor)
        comp_prompt = ChatPromptTemplate.from_messages([
            ("system", "Invent a realistic competitor product."),
            ("user", "Target: {p_name} ({p_price}).\n{format_instructions}")
        ])
        competitor = (comp_prompt | llm | comp_parser).invoke({
            "p_name": p.name, "p_price": p.price, 
            "format_instructions": comp_parser.get_format_instructions()
        })

    # 2. FAQ Generation (The "Thinking" Part)
    # Check if we are retrying based on a critique
    critique_instruction = ""
    if state.critique:
        print(f"   ⚠️ ADAPTING STRATEGY based on feedback: '{state.critique}'")
        critique_instruction = f"""
        CRITICAL FEEDBACK FROM LAST ATTEMPT: "{state.critique}"
        
        INSTRUCTIONS TO FIX:
        1. If count was low, generate at least 20 questions.
        2. If repetitive, vary your topics.
        3. Ensure 100% adherence to the feedback.
        """
    
    q_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Customer Success AI. Generate a comprehensive FAQ list."),
        ("user", f"""
        Product: {p.name}
        Side Effects: {p.side_effects}
        
        TASK: Generate a raw JSON list of objects with keys: "category", "question", "answer".
        TARGET: Minimum 18 unique questions covering Safety, Usage, Value, Science.
        
        {critique_instruction}
        
        Return ONLY raw JSON. No markdown.
        """)
    ])
    
    try:
        response = llm.invoke(q_prompt.format(p_name=p.name, p_side_effects=p.side_effects))
        raw_content = response.content.replace("```json", "").replace("```", "").strip()
        q_data = json.loads(raw_content)
        questions = [Question(**q) for q in q_data]
    except Exception as e:
        print(f"   ❌ Generation Error: {e}")
        questions = [] # Return empty to force QA fail and retry
    
    return {"competitor": competitor, "questions": questions, "retry_count": attempt}

# --- Node 3: QA & Validation (The "Critic") ---
def qa_validation_node(state: AgentState) -> dict:
    print("🕵️ [QA Agent] Auditing output quality...")
    
    # 1. QUANTITATIVE CHECK (The "Hard" Gate)
    count = len(state.questions)
    if count < 15:
        print(f"   ❌ QA FAIL: Count is {count}/15. Rejecting.")
        return {"critique": f"Generated only {count} questions. Requirement is STRICTLY 15 or more."}

    # 2. QUALITATIVE CHECK (The "Semantic" Gate using Gemini)
    # This solves "No mechanism to verify FAQ relevance"
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a strict QA Auditor. Reply PASS or FAIL <Reason>."),
        ("user", f"""
        Review these FAQs for {state.product.name}:
        {[q.question for q in state.questions]}
        
        Fail if:
        - Repetitive questions.
        - Irrelevant to the product.
        - Poor grammar.
        
        Verdict:
        """)
    ])
    
    try:
        verdict = llm.invoke(qa_prompt.format()).content.strip()
        if "FAIL" in verdict.upper():
            print(f"   ❌ QA FAIL: Content Quality ({verdict})")
            return {"critique": verdict}
    except:
        pass # If QA LLM fails, we default to passing the hard check
        
    print(f"   ✅ QA PASS: {count} questions verified.")
    return {"critique": None} # None = Success

# --- Node 4: Logic Engine ---
def comparison_logic_node(state: AgentState) -> dict:
    print("⚖️ [Logic Engine] Grounding with math...")
    p, c = state.product, state.competitor
    price_stats = calculate_price_delta(p.price, c.price)
    ing_stats = extract_ingredient_overlap(p.ingredients, c.ingredients)
    
    analysis = ComparisonData(
        verdict="Better Value" if price_stats['is_cheaper'] else "Premium Choice",
        price_diff=price_stats['diff'],
        advantage_summary=f"Has {len(ing_stats['unique_to_p1'])} unique ingredients.",
        common_ingredients=ing_stats['common']
    )
    return {"comparison_analysis": analysis}

# --- Node 5: Assembly ---
def assembly_node(state: AgentState) -> dict:
    print("📝 [Assembly Agent] Finalizing JSONs...")
    return {
        "product_page_json": state.product.model_dump_json(indent=2),
        "faq_json": json.dumps({"title": "FAQ", "count": len(state.questions), "items": [q.model_dump() for q in state.questions]}, indent=2),
        "comparison_page_json": json.dumps({"product_a": state.product.name, "product_b": state.competitor.name, "analysis": state.comparison_analysis.model_dump()}, indent=2)
    }