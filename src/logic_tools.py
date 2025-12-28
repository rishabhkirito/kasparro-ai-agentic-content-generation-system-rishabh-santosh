def calculate_price_delta(p1_price: float, p2_price: float) -> dict:
    """Deterministic math logic for price comparison."""
    diff = p1_price - p2_price
    return {
        "diff": diff,
        "is_cheaper": diff < 0,
        "percent_diff": round((diff / p2_price) * 100, 1) if p2_price else 0
    }

def extract_ingredient_overlap(list1: list, list2: list) -> dict:
    """Deterministic set logic for ingredient analysis."""
    s1 = set(x.lower().strip() for x in list1)
    s2 = set(x.lower().strip() for x in list2)
    return {
        "common": list(s1.intersection(s2)),
        "unique_to_p1": list(s1 - s2),
        "unique_to_p2": list(s2 - s1)
    }