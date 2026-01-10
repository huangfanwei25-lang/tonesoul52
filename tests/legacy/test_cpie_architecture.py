
import sys
import os

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def verify_architecture():
    print("🏗️ Verifying TAE-01 Architecture (CPIE)...")
    
    try:
        # 1. Test Codex
        from modules.codex.dictionary import Dimension, Grade
        print(f"✅ Codex Loaded: {Dimension.STABILITY.value}, Grade={Grade.HIGH.value}")
        
        # 2. Test Telemetry (STREI)
        from body.sensors.telemetry import STREI
        v = STREI(Stability=0.8, Tension=0.5, Responsibility=0.2, Ethics=0.95, Intent=0.8)
        print(f"✅ Telemetry: {v}")
        
        # 3. Test Guardian (Ethics)
        from modules.ethics.guardian import Guardian
        g = Guardian() # Should load YAML
        decision = g.evaluate(v.to_dict())
        print(f"✅ Guardian Decision: {decision.outcome} (Reason: {decision.reason})")
        # Expect BLOCK because R=0.2 < 0.6
        if decision.outcome == "BLOCK" and "Responsibility" in decision.reason:
            print("   -> Correctly BLOCKED due to low Responsibility.")
        else:
            print("   -> ⚠️ Unexpected Decision Logic!")
            
        # 4. Test Ledger (Protocol)
        from modules.protocol.ledger import StepLedger
        ledger = StepLedger("tests/test_ledger.jsonl")
        h = ledger.commit("TEST_POLICY", {"S":0.8}, "BLOCK", "Test Entry")
        print(f"✅ Ledger: Committed entry, hash={h[:8]}...")
        
        # 5. Test Integrity
        from modules.integrity.monitor import IntegrityMonitor
        valid = IntegrityMonitor.verify_ledger_chain("tests/test_ledger.jsonl")
        print(f"✅ Integrity: Chain Valid? {valid}")

        # Clean up
        if os.path.exists("tests/test_ledger.jsonl"):
            os.remove("tests/test_ledger.jsonl")
            
        return True

    except Exception as e:
        print(f"❌ Verification Failed: {e}")
        return False

if __name__ == "__main__":
    verify_architecture()
