
import subprocess
import sys

def run_test(name, command):
    print(f"\nExample Running: {name}...")
    result = subprocess.run(command, shell=True)
    if result.returncode == 0:
        print(f"✅ {name}: PASS")
    else:
        print(f"❌ {name}: FAIL")

if __name__ == "__main__":
    print("=== ToneSoul System Verification ===")
    
    # 1. Architecture Check
    run_test("Architecture (CPIE)", "python tests/test_cpie_architecture.py")
    
    # 2. Sensor Check
    run_test("Active Telemetry (L3)", "python tests/test_dynamic_telemetry.py")
    
    # 3. Integration Check
    run_test("Spine Controller (L1)", "python tests/test_spine_integration.py")
    
    print("\n=== Verification Complete ===")
