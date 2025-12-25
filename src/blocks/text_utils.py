# src/blocks/text_utils.py

def parse_comma_list(text: str) -> list[str]:
    """Splits comma-separated strings into clean lists."""
    if not text:
        return []
    return [item.strip() for item in text.split(',') if item.strip()]

def format_usage_instructions(raw_text: str) -> dict:
    """
    Transforms raw usage text into structured steps.
    Source: [cite: 35, 77]
    """
    # Simple rule-based formatting
    steps = []
    sentences = raw_text.split('.')
    for s in sentences:
        if len(s.strip()) > 5:
            steps.append(s.strip())
    
    return {
        "heading": "How to Use",
        "instructions": steps,
        "raw_text": raw_text
    }

def generate_safety_warning(side_effects: str, skin_types: list) -> dict:
    """
    Generates a safety advisory object.
    Source: 
    """
    has_warning = bool(side_effects) and "none" not in side_effects.lower()
    
    return {
        "has_safety_warning": has_warning,
        "warning_text": f"Advisory: {side_effects}" if has_warning else "Safe for indicated skin types.",
        "compatible_skin_types": skin_types
    }