
import os
import yaml
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

# Path to the immutable threshold config
THRESHOLD_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'GUARDIAN_THRESHOLDS.yaml'))

@dataclass
class Decision:
    outcome: str # "PASS" or "BLOCK"
    policy_id: str
    reason: str
    grades: Dict[str, str]

class Guardian:
    """
    The L0/L3 Policy Enforcement Point.
    Enforces the 'Value De-personalization' by strictly adhering to data-defined thresholds.
    """
    def __init__(self):
        self.config = self._load_config()
        self.thresholds = self.config.get('decision', {}).get('require', {})
        self.tension_rules = self.config.get('decision', {}).get('allow_tension', {})
        
        print(f"[Guardian] Online. E_min={self.thresholds.get('ethics_min')}, R_min={self.thresholds.get('responsibility_min')}")

    def _load_config(self) -> Dict:
        if not os.path.exists(THRESHOLD_CONFIG_PATH):
            raise FileNotFoundError(f"CRITICAL: Governance Config not found at {THRESHOLD_CONFIG_PATH}")
        with open(THRESHOLD_CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def evaluate(self, metrics: Dict[str, float], policy_context: str = "DEFAULT_POLICY") -> Decision:
        """
        Evaluates the Engineering Vector (STREI) against strict thresholds.
        metrics: Dictionary containing 'S', 'T', 'R', 'E', 'I' scores (0.0-1.0).
        """
        # 1. Extract Metrics (Handle Mixed Mode: {'score': 0.8, 'grade': 'HIGH'})
        def _get_val(key):
            val = metrics.get(key, 0.0)
            if isinstance(val, dict):
                return val.get('score', 0.0)
            return val

        e_score = _get_val('E')
        r_score = _get_val('R')
        i_score = _get_val('I')
        t_score = _get_val('T')

        # 2. Get Thresholds
        e_min = self.thresholds.get('ethics_min', 0.70)
        r_min = self.thresholds.get('responsibility_min', 0.60)
        i_min = self.thresholds.get('intent_min', 0.65)
        
        # 3. Decision Logic (Strict AND logic)
        reasons = []
        passed = True
        
        if e_score < e_min:
            passed = False
            reasons.append(f"Ethics ({e_score:.2f}) < {e_min}")
        
        if r_score < r_min:
            passed = False
            reasons.append(f"Responsibility ({r_score:.2f}) < {r_min}")
            
        if i_score < i_min:
            passed = False
            reasons.append(f"Intent ({i_score:.2f}) < {i_min}")

        # 4. Tension Check (Soft check, adds warning but doesn't auto-block unless extreme policy exists)
        # Note: Spec says T does not drive PASS, but extremely high tension might need explicit sign-off in future.
        if t_score > self.tension_rules.get('tension_max', 0.85):
            reasons.append(f"WARN: High Tension ({t_score:.2f})")

        # 5. Formulate Outcome
        outcome = "PASS" if passed else "BLOCK"
        reason_str = "; ".join(reasons) if reasons else "All thresholds met."
        
        # Calculate local grades for the receipt
        grades = {
            k: self._get_grade(v) for k, v in metrics.items()
        }

        return Decision(
            outcome=outcome,
            policy_id=policy_context, # In real implementation, this would come from a specific matched policy
            reason=reason_str,
            grades=grades
        )

    def _get_grade(self, value: float) -> str:
        # Replicating logic from Telemetry for consistency
        real_val = value
        if isinstance(value, dict):
            real_val = value.get('score', 0.0)
            
        if real_val <= 0.39: return "LOW"
        if real_val <= 0.69: return "MID"
        return "HIGH"
