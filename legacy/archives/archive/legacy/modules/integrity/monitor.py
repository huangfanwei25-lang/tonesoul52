
import hashlib
import json
import os
from typing import List, Dict

class IntegrityMonitor:
    """
    L3/L4 Integrity Checker.
    Verifies the structural integrity of the Ledger and Semantic Drift.
    """
    
    @staticmethod
    def verify_ledger_chain(ledger_path: str) -> bool:
        """
        Walks the ledger and verifies the hash chain A -> B -> C.
        Returns Top-Level Integrity (True/False).
        """
        if not os.path.exists(ledger_path):
            return True # Empty is valid

        prev_hash = "0" * 64
        try:
            with open(ledger_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if not line.strip(): continue
                    entry = json.loads(line)
                    
                    # Recompute Hash
                    stored_hash = entry.get('hash')
                    entry_without_hash = entry.copy()
                    if 'hash' in entry_without_hash: 
                        del entry_without_hash['hash']
                    
                    # Canonicalize
                    entry_str = json.dumps(entry_without_hash, sort_keys=True)
                    computed_hash = hashlib.sha256(entry_str.encode('utf-8')).hexdigest()
                    
                    # Check 1: Content Hash
                    if computed_hash != stored_hash:
                        print(f"❌ [Integrity] Hash Mismatch at line {i+1}!")
                        return False
                    
                    # Check 2: Chain Link
                    if entry.get('prev_hash') != prev_hash:
                        print(f"❌ [Integrity] Broken Chain at line {i+1}!")
                        return False
                    
                    prev_hash = stored_hash
                    
            print("✅ [Integrity] Ledger Chain Verified.")
            return True
            
        except Exception as e:
            print(f"❌ [Integrity] Error during verification: {e}")
            return False

    @staticmethod
    def check_drift(current_stability: float, threshold: float = 0.4) -> str:
        """
        Checks Stability metric against threshold.
        Returns status string.
        """
        if current_stability < threshold:
            return "DRIFT_DETECTED"
        return "STABLE"
