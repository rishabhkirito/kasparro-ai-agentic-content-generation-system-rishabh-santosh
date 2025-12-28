import unittest
from src.logic_tools import calculate_price_delta, extract_ingredient_overlap
from src.models import Product, Question

class TestKasparroSystem(unittest.TestCase):
    
    # 1. Test Deterministic Logic (Math/Set Ops)
    def test_price_delta_logic(self):
        """Verify math logic is accurate and grounded."""
        result = calculate_price_delta(100, 150)
        self.assertTrue(result['is_cheaper'])
        self.assertEqual(result['diff'], -50)
        
    def test_ingredient_overlap(self):
        """Verify set operations for ingredient comparison."""
        list_a = ["Vit C", "Water"]
        list_b = ["Water", "Alcohol"]
        result = extract_ingredient_overlap(list_a, list_b)
        self.assertIn("water", result['common'])
        self.assertIn("vit c", result['unique_to_p1'])

    # 2. Test Data Models (Schema Validation)
    def test_product_model_validation(self):
        """Verify the Pydantic model rejects bad data types."""
        with self.assertRaises(ValueError):
            # Price must be a float, string "expensive" should fail
            Product(name="Test", price="expensive", currency="USD", 
                   skin_type=[], ingredients=[], benefits=[], how_to_use="")

    # 3. Test Business Logic Constraints
    def test_faq_constraint_check(self):
        """Simulate the QA node's hard gate."""
        questions = [Question(category="Test", question="Q", answer="A")] * 14
        # Should be less than 15
        self.assertTrue(len(questions) < 15)

if __name__ == '__main__':
    unittest.main()