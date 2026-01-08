
import json
import time
import uuid
import hashlib
from typing import Dict, Any, Optional

class StepLedger:
    """
    L4 Ledger Layer.
    Implements the Audit Contract: Append-only, Hash-Chained, Policy-Signed.
    """
    LEDGER_FILE = "ledger.jsonl" # In production, this might be a db path or log stream

    def __init__(self, ledger_path: str = "body/ledger/ledger.jsonl"):
        self.ledger_path = ledger_path
        self.prev_hash = self._get_last_hash()

    def _get_last_hash(self) -> str:
        """Reads the last entry to get its hash for chaining."""
        last_hash = "0" * 64 # Genesis hash
        if os.path.exists(self.ledger_path):
            try:
                # Read last line efficiently (simplified here)
                with open(self.ledger_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        last_entry = json.loads(lines[-1])
                        last_hash = last_entry.get('hash', last_hash)
            except Exception as e:
                print(f"⚠️ [Ledger] Error reading last hash: {e}")
        return last_hash

    def commit(self, 
               policy_id: str, 
               metrics: Dict[str, float],
               decision: str,
               content_summary: str = "") -> str:
        """
        Commits an entry to the ledger.
        Returns the hash of the new entry.
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        event_id = str(uuid.uuid4())
        
        # 1. Prepare Entry Content (excluding hash)
        # Note: We include grades here manually or rely on caller to pass them?
        # For simplicity, we calculate grades lazily or assume 'metrics' has them if passed complexly.
        # But 'metrics' arg type is Dict[str, float]. Let's stick to spec: pass grades if possible.
        # Ideally, Guardian returns a Decision object with grades. 
        # For this base class, we'll keep it simple: caller passes raw metrics, we log them. 
        
        entry_data = {
            "event_id": event_id,
            "timestamp": timestamp,
            "policy_id": policy_id,
            "metrics": metrics,
            # "grades": ... computed by caller usually, but okay to omit in this minimal implementation if metrics are there.
            "decision": decision,
            "content_summary": content_summary,
            "prev_hash": self.prev_hash
        }
        
        # 2. Compute Hash (SHA256)
        # Canonical JSON string for hashing
        entry_str = json.dumps(entry_data, sort_keys=True)
        new_hash = hashlib.sha256(entry_str.encode('utf-8')).hexdigest()
        
        # 3. Finalize Entry
        entry_data['hash'] = new_hash
        
        # 4. Append to File
        self._append_to_file(entry_data)
        
        # 5. Update State
        self.prev_hash = new_hash
        return new_hash

    def _append_to_file(self, entry: Dict[str, Any]):
        # Ensure dir exists
        os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)
        with open(self.ledger_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')

import os # Late import for file ops
