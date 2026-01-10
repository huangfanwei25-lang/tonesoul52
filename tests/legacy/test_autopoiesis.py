import os
import shutil
import pytest
import sys
from body.surgeon.surgeon import Surgeon

# Broken Code (Syntax Error)
BROKEN_CODE = "print('Hello World'"

class TestAutopoiesis:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        # Setup: Create a broken file
        self.test_file = "body/BROKEN_TEST_FILE.py"
        self.abs_path = os.path.abspath(self.test_file)
        
        with open(self.abs_path, "w", encoding="utf-8") as f:
            f.write(BROKEN_CODE)
            
        yield
        
        # Teardown: Cleanup
        if os.path.exists(self.abs_path):
            os.remove(self.abs_path)
        if os.path.exists(self.abs_path + ".bak"):
            os.remove(self.abs_path + ".bak")

    def test_surgeon_fixes_broken_code(self):
        """
        Verifies that Surgeon can:
        1. Identify the issue (provided by us).
        2. Generate a fix (via LLM).
        3. Validate it in Sandbox (Syntax Check).
        4. Apply the fix.
        """
        # Initialize Surgeon with Local Brain (Ollama)
        # Note: This assumes 'gemma3:4b' or similar is running perfectly.
        # If the model is dumb, it might fail to fix syntax.
        # But we are testing the PIPELINE, not the model IQ.
        surgeon = Surgeon(provider="ollama")
        
        # Operate
        print(f"\n[Test] Operating on {self.test_file}...")
        result = surgeon.operate(self.test_file, "Fix the syntax error (missing closing parenthesis).")
        
        print(f"[Test] Result: {result}")
        
        # Assert Operation Success
        assert "Operation Successful" in result
        
        # Assert Backup Created
        assert os.path.exists(self.test_file + ".bak")
        
        # Assert Content Fixed
        with open(self.abs_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        print(f"[Test] Fixed Content: {content}")
        assert "print('Hello World')" in content or 'print("Hello World")' in content
        assert content.strip().endswith(")") # Rudimentary check for syntax fix
