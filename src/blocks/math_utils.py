# src/blocks/math_utils.py

def calculate_price_diff(price_a: float, price_b: float) -> dict:
    """
    Calculates value proposition vs competitor.
    Source: [cite: 78]
    """
    diff = price_a - price_b
    if diff < 0:
        verdict = "Better Value"
        msg = f"Save {abs(diff)} compared to competitor"
    elif diff > 0:
        verdict = "Premium Choice"
        msg = f"Invests {abs(diff)} more for premium ingredients"
    else:
        verdict = "Equal Price"
        msg = "Same price point"

    return {
        "difference": diff,
        "verdict": verdict,
        "message": msg
    }

def compare_ingredients(list_a: list, list_b: list) -> dict:
    """
    Analyzes ingredient overlap.
    Source: [cite: 78]
    """
    set_a = set([x.lower() for x in list_a])
    set_b = set([x.lower() for x in list_b])
    
    common = list(set_a.intersection(set_b))
    unique_a = list(set_a - set_b)
    
    return {
        "common_ingredients": common,
        "our_unique_advantages": unique_a,
        "competitor_ingredients": list(set_b)
    }