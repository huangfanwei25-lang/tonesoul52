import os
import sys

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from body.surgeon.sandbox import Sandbox


def test_fortress():
    print("🚀 [Verification] Initializing Fortress Stress Test...")
    sb = Sandbox()

    # 1. Setup a dummy file
    target = os.path.join("temp", "test_file.py")
    os.makedirs("temp", exist_ok=True)
    with open(target, "w") as f:
        f.write("print('Hello from the Fortress')")

    sb.setup(target)

    # 2. Test Normal Execution
    print("\n--- Test 1: Normal Execution ---")
    info = sb.verify("python3 test_file.py")
    print(f"Result: {'PASS' if info[0] else 'FAIL'}")
    print(f"Log: {info[1]}")

    # 3. Test Timeout Execution (Infinite Loop)
    print("\n--- Test 2: Timeout Enforcement (Infinite Loop) ---")
    sb.apply_patch(
        os.path.join(sb.sandbox_dir, "test_file.py"), "import time\nwhile True: time.sleep(1)"
    )
    info = sb.verify("python3 test_file.py", timeout=5)  # Short timeout for test
    print(f"Result: {'PASS' if info[0] else 'FAIL'} (Expected FAIL/Timeout)")
    print(f"Log: {info[1]}")

    sb.teardown()
    print("\n🏁 [Verification] Stress Test Complete.")


if __name__ == "__main__":
    test_fortress()
