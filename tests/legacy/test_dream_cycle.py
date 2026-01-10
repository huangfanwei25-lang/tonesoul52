import unittest
import sys
import os
import shutil
import time

# Add root to path
sys.path.append(os.getcwd())

from body.dream.weaver import DreamWeaver
from body.memory.hippocampus import MemoryConsolidator

class TestDreamCycle(unittest.TestCase):
    def test_simulation_flow(self):
        print("\n[Test] Starting Dream Cycle Simulation...")
        
        # 1. Setup minimal memory
        hippocampus = MemoryConsolidator()
        # Inject a fake memory
        hippocampus.engrave("Project Titan: Autonomous Drone Swarm for Agriculture", importance=0.9)
        
        # 2. Initialize DreamWeaver
        weaver = DreamWeaver(hippocampus)
        
        # 3. Enter REM (Short duration for test)
        insights = weaver.enter_rem_cycle(duration_seconds=10)
        
        # 4. Assertions
        self.assertGreater(len(insights), 0, "Should generate at least one insight from the strong memory.")
        insight = insights[0]
        
        print(f"Topic: {insight['topic']}")
        print(f"Structure Length: {len(insight['simulation']['structure'])}")
        
        self.assertIn("vision", insight['simulation'])
        self.assertIn("risks", insight['simulation'])
        self.assertIn("structure", insight['simulation'])

if __name__ == '__main__':
    unittest.main()
