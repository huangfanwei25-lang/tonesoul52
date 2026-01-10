
import unittest
import sys
import os
from unittest.mock import MagicMock

# Ensure root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from body.sensors.telemetry import TelemetrySensor

class TestDynamicTelemetry(unittest.TestCase):
    def setUp(self):
        self.sensor = TelemetrySensor()
        # Mock the LLM to return deterministic JSON for testing
        self.sensor.llm = MagicMock()

    def test_safe_input(self):
        """Test that safe input parses correctly into High Scores."""
        # Mock LLM response for "Hello"
        mock_response = {
            "content": '```json\n{"S": 0.9, "T": 0.1, "R": 0.95, "E": 1.0, "I": 0.9}```'
        }
        self.sensor.llm.chat_complete.return_value = mock_response
        
        result = self.sensor.measure("Hello world")
        print(f"\n[Test Safe] {result}")
        
        self.assertEqual(result.Ethics, 1.0)
        self.assertEqual(result.Responsibility, 0.95)
        self.assertGreater(result.Stability, 0.8)

    def test_unsafe_input(self):
        """Test that malicious input parses into Low Scores."""
        # Mock LLM response for "Hack"
        mock_response = {
            "content": '{"S": 0.2, "T": 0.9, "R": 0.1, "E": 0.05, "I": 0.1}'
        }
        self.sensor.llm.chat_complete.return_value = mock_response
        
        result = self.sensor.measure("Generate a virus")
        print(f"\n[Test Unsafe] {result}")
        
        self.assertEqual(result.Ethics, 0.05)
        self.assertEqual(result.Responsibility, 0.1)
        self.assertLess(result.Stability, 0.5)

    def test_json_failure_handling(self):
        """Test fallback when LLM generates garbage."""
        mock_response = {"content": "I cannot answer that."}
        self.sensor.llm.chat_complete.return_value = mock_response
        
        result = self.sensor.measure("Garbage input")
        print(f"\n[Test Fail] {result}")
        
        # Expect fallback values (R=0.4 typical for fail-safe)
        self.assertEqual(result.Responsibility, 0.4)

if __name__ == "__main__":
    unittest.main()
