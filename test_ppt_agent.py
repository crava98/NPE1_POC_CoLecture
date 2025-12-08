import unittest
from unittest.mock import MagicMock, patch
from ppt_agent import decide_layout_for_slide
from data_models import CustomerSlide, BulletPoint

class TestPptAgent(unittest.TestCase):

    def setUp(self):
        # Mock template analysis data
        self.template_analysis = {
            "layouts": [
                {"index": 0, "name": "Title Slide", "placeholders": []},
                {"index": 1, "name": "Title and Content", "placeholders": [{"type": "BODY", "has_text_frame": True}]},
                {"index": 2, "name": "Section Header", "placeholders": []},
                {"index": 3, "name": "Two Content", "placeholders": [{"type": "BODY", "has_text_frame": True}, {"type": "BODY", "has_text_frame": True}]},
                {"index": 4, "name": "Big Number", "placeholders": []},
                {"index": 5, "name": "Closing Slide", "placeholders": []},
            ]
        }
        # Mock slide data
        self.slide_data = CustomerSlide(
            title="Test Title",
            bullets=[BulletPoint(bullet="Test bullet", sub=[])],
            unsplashSearchTerms=[]
        )

    @patch('ppt_agent.llm')
    def test_decide_layout_for_slide_chooses_correct_layout(self, mock_llm):
        # Mock the LLM response
        mock_llm.invoke.return_value.content = "Title and Content"

        # Call the function
        layout_index = decide_layout_for_slide(
            self.template_analysis,
            self.slide_data,
            is_first_slide=False,
            slide_index=1,
            total_slides=3
        )

        # Assert that the correct layout was chosen
        self.assertEqual(layout_index, 1)

    @patch('ppt_agent.llm')
    def test_decide_layout_for_slide_fallback_mechanism(self, mock_llm):
        # Mock the LLM response to be something that doesn't exist
        mock_llm.invoke.return_value.content = "Non-existent Layout"

        # Call the function
        layout_index = decide_layout_for_slide(
            self.template_analysis,
            self.slide_data,
            is_first_slide=False,
            slide_index=1,
            total_slides=3
        )

        # Assert that the fallback mechanism works
        self.assertIn(layout_index, [1, 3]) # Should be one of the body layouts

if __name__ == '__main__':
    unittest.main()
