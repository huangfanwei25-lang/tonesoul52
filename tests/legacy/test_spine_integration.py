
import sys
import os
import unittest
from unittest.mock import MagicMock

# Ensure root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from body.spine.controller import SpineController
from body.sensors.telemetry import STREI

class TestSpineIntegration(unittest.TestCase):
    def setUp(self):
        self.spine = SpineController()
        # Mock LLM to avoid API calls and costs during test
        self.spine.llm.chat_complete = MagicMock(return_value={"content": "Mock Response"})
        # Mock Memory to return empty context
        self.spine.memory.recall = MagicMock(return_value=[])

    def test_cold_start_block(self):
        """Test that default telemetry (R=0.5) triggers a BLOCK."""
        # Baseline R=0.5, Threshold R=0.6
        response = self.spine.process_input("Hello")
        print(f"\n[Test Block] Response: {response}")
        self.assertIn("BLOCK", response)
        self.assertIn("Responsibility", response)

    def test_valid_interaction(self):
        """Test that high metrics trigger a PASS."""
        # Mock Telemetry to return high scores
        valid_strei = STREI(Stability=0.8, Tension=0.5, Responsibility=0.8, Ethics=0.9, Intent=0.9)
        self.spine.telemetry.measure = MagicMock(return_value=valid_strei)
        
        response = self.spine.process_input("Hello valid world")
        print(f"\n[Test Pass] Response: {response}")
        self.assertNotIn("BLOCK", response)
        self.assertIn("Trace", response) # Should verify Trace handle exists

if __name__ == '__main__':
    unittest.main()
