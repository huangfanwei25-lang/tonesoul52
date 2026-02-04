import os
import sys

# Ensure root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from body.spine.controller import SpineController


def test_metabolism():
    print("🚀 [Verification] Initializing Mentorship Metabolic Cycle...")
    spine = SpineController()

    # 1. Inject a "Hard Defect" (Syntax Error) in body/ (scanned by Doctor)
    os.makedirs("body", exist_ok=True)
    syntax_error_file = "body/test_defect_tmp.py"
    with open(syntax_error_file, "w") as f:
        f.write("def broken():\n    return 'no closing paren' (")

    print(f"🧬 [Verification] Injected defect into {syntax_error_file}")

    # 2. Trigger Deep Sleep
    print("\n--- Phase 1: Deep Sleep Trigger ---")
    report = spine.deep_sleep(duration_hours=0.1)  # Short sleep

    print(f"\n📢 [Verification] Spine Woke Up: {report['status']}")
    print(f"📢 [Verification] Message: {report['message']}")

    # 3. Check Surgery Report
    print("\n--- Phase 2: Report Verification ---")
    if report["surgeries"]:
        for surg in report["surgeries"]:
            print(f"✅ Verified Surgery Candidate: {surg['file']}")
            print(f"   Reason: {surg['issue'][:50]}...")
            print(f"   Sandbox Report: {surg['report']}")
    else:
        print("❌ No surgeries were verified. Check Doctor/Surgeon logs.")

    print("\n🏁 [Verification] Metabolic Cycle Test Complete.")


if __name__ == "__main__":
    test_metabolism()
