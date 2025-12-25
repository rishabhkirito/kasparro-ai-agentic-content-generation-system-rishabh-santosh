# src/agents/faq_agent.py
import json
from src.models import Question
from src.templates.schemas import FAQTemplate

class FAQAgent:
    """
    Responsibility: Organize questions and render the FAQ Page using a template.
    Satisfies Requirement: Modular agent with clear input/output[cite: 61, 64].
    """
    
    def build(self, questions: list[Question]) -> str:
        """
        Input: List of Question objects.
        Output: JSON string representing the FAQ page.
        """
        # 1. Logic: Group questions by category (Data Transformation)
        categorized_questions = {}
        for q in questions:
            if q.category not in categorized_questions:
                categorized_questions[q.category] = []
            
            # Formatting the Q&A pair for the template
            categorized_questions[q.category].append({
                "question": q.question_text,
                "answer": q.answer_text
            })
            
        # 2. Presentation: Render using the strictly defined Template
        # This ensures the output always matches the defined schema.
        page_content = FAQTemplate.render(categorized_questions)
        
        # 3. Serialization
        return json.dumps(page_content, indent=2)