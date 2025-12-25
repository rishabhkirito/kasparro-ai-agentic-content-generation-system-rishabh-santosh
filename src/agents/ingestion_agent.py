# src/agents/ingestion_agent.py
from src.models import Product
from src.blocks.text_utils import parse_comma_list
import re

class DataIngestionAgent:
    """
    Responsibility: Parse raw unstructured text into Product Model.
    Source: [cite: 26, 27]
    """
    def parse(self, raw_text: str) -> Product:
        data = {}
        
        # Simple line-by-line parsing logic
        lines = raw_text.strip().split('\n')
        for line in lines:
            if ':' in line:
                key, val = line.split(':', 1)
                data[key.strip()] = val.strip()

        # Handle Price specifically (removing currency symbol)
        raw_price = data.get('• Price', '0').replace('₹', '').strip()
        
        return Product(
            name=data.get('Product Name', 'Unknown'),
            price=float(raw_price) if raw_price.replace('.','').isdigit() else 0.0,
            currency='INR',
            concentration=data.get('Concentration'),
            skin_type=parse_comma_list(data.get('Skin Type', '')),
            ingredients=parse_comma_list(data.get('Key Ingredients', '')),
            benefits=parse_comma_list(data.get('Benefits', '')),
            how_to_use=data.get('How to Use', ''),
            side_effects=data.get('Side Effects')
        )