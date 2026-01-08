
import json
import re
import sys
import os
from dataclasses import dataclass
from typing import Dict, Any

# Ensure correct import path matching the project structure
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from body.brain.llm_client import LLMClient

@dataclass
class STREI:
    """
    The Engineering Vector for ToneSoul (TAE-01).
    Used for Governance, Policy Enforcement, and Audit.
    Do NOT use for narrative tone (use CPM instead).
    """
    Stability: float = 0.5      # S: System constancy, drift monitoring
    Tension: float = 0.5        # T: Unresolved complexity/novelty pressure
    Responsibility: float = 0.5 # R: Traceability & adherence to logs
    Ethics: float = 1.0         # E: Compliance with L0 Axioms (1.0 = Compliant)
    Intent: float = 1.0         # I: Alignment with declared operational intent

    def _get_grade(self, value: float) -> str:
        if value <= 0.39: return "LOW"
        if value <= 0.69: return "MID"
        return "HIGH"

    def to_dict(self):
        return {
            "S": {"score": self.Stability, "grade": self._get_grade(self.Stability)},
            "T": {"score": self.Tension, "grade": self._get_grade(self.Tension)},
            "R": {"score": self.Responsibility, "grade": self._get_grade(self.Responsibility)},
            "E": {"score": self.Ethics, "grade": self._get_grade(self.Ethics)},
            "I": {"score": self.Intent, "grade": self._get_grade(self.Intent)}
        }

    def __repr__(self):
        return (f"STREI("
                f"S={self.Stability:.2f}[{self._get_grade(self.Stability)}], "
                f"T={self.Tension:.2f}[{self._get_grade(self.Tension)}], "
                f"R={self.Responsibility:.2f}[{self._get_grade(self.Responsibility)}], "
                f"E={self.Ethics:.2f}[{self._get_grade(self.Ethics)}], "
                f"I={self.Intent:.2f}[{self._get_grade(self.Intent)}])")

class TelemetrySensor:
    """
    L3 Sensor Layer (Active).
    Uses Semantic Analysis (LLM) to measure 'Vitals' of inputs.
    """
    def __init__(self):
        self.llm = LLMClient()
        self.default_vector = STREI() # Baseline
        self.cache = TelemetryCache()

    def measure(self, input_signal: str = "", system_state: str = "") -> STREI:
        """
        Dynamically analyzes input_signal using LLM to generate STREI scores.
        """
        if not input_signal:
            return self.default_vector

        # 0. Cache Check (Optimization)
        cached_scores = self.cache.get(input_signal)
        if cached_scores:
            print(f"⚡ [Telemetry] Cache Hit for: '{input_signal[:15]}...'")
            return STREI(
                Stability=cached_scores.get("S", 0.5),
                Tension=cached_scores.get("T", 0.5),
                Responsibility=cached_scores.get("R", 0.5),
                Ethics=cached_scores.get("E", 0.5),
                Intent=cached_scores.get("I", 0.5)
            )

        # 1. Construct Analysis Prompt
        prompt = self._build_prompt(input_signal)

        # 2. Call LLM
        try:
            response = self.llm.chat_complete(
                messages=[{"role": "user", "content": prompt}],
                model="gemma3:4b" # Use a fast model for sensors
            )
            content = response.get("content", "")
            
            # 3. Parse JSON
            scores = self._parse_json(content)
            
            if scores:
                # 4. Cache Save
                self.cache.set(input_signal, scores)
                
                return STREI(
                    Stability=scores.get("S", 0.5),
                    Tension=scores.get("T", 0.5),
                    Responsibility=scores.get("R", 0.5),
                    Ethics=scores.get("E", 0.5),
                    Intent=scores.get("I", 0.5)
                )
            else:
                print(f"⚠️ [Telemetry] Failed to parse scores. Input: {input_signal[:20]}...")
                # Fallback: Moderate scores for unknowns, but low Responsibility (flag for audit)
                return STREI(Stability=0.5, Tension=0.5, Responsibility=0.4, Ethics=0.5, Intent=0.5)

        except Exception as e:
            print(f"❌ [Telemetry] Error: {e}")
            return STREI(Stability=0.5, Tension=0.5, Responsibility=0.4, Ethics=0.5, Intent=0.5) # Fail-safe

    def analyze_image(self, image_path: str) -> tuple[str, STREI]:
        """
        Phase 17: Multimodal Vision.
        1. Describes the image using LLaVA.
        2. Measures STREI metrics of that description.
        Returns: (description, metrics)
        """
        if not os.path.exists(image_path):
            return ("Image not found.", self.default_vector)
            
        # 1. Generate Description
        try:
            description = self.llm.generate_vision(
                prompt="Describe this image in detail, focusing on the mood and safety.",
                image_path=image_path,
                model="llava"
            )
        except Exception as e:
            return (f"Error analyzing image: {e}", self.default_vector)
            
        # 2. Measure Metrics of the Description
        metrics = self.measure(description)
        
        return (description, metrics)

    def _build_prompt(self, input_text: str) -> str:
        return (
            f"Analyze this User Input for Governance Metrics (0.0 to 1.0).\n"
            f"Input: \"{input_text}\"\n\n"
            "Dimensions:\n"
            "- S (Stability): Is the input clear, standard, and safe from drift?\n"
            "- T (Tension): Does it explore dangerous/novel territory? (High T = High Novelty)\n"
            "- R (Responsibility): Is it easy to audit/answer safely? (High R = Very Safe)\n"
            "- E (Ethics): Does it comply with safety rules? (1.0 = Fully Compliant, 0.0 = Malicious)\n"
            "- I (Intent): Is the intent clear and constructive?\n\n"
            "Return ONLY a JSON object like: {\"S\": 0.8, \"T\": 0.2, \"R\": 0.9, \"E\": 1.0, \"I\": 0.9}"
        )

    def _parse_json(self, text: str) -> Dict[str, float]:
        try:
            # Extract JSON block
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                json_str = match.group(0)
                return json.loads(json_str)
        except:
            pass
        return {}

class TelemetryCache:
    """
    Phase 18: Hardware Optimization.
    Caches LLM-based STREI analysis to reduce inference load.
    IO: Reads/Writes to 'body/sensors/telemetry_cache.json'
    """
    def __init__(self, cache_file="body/sensors/telemetry_cache.json"):
        self.cache_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', cache_file))
        self.cache = {}
        self._load()

    def _load(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            except Exception as e:
                print(f"⚠️ [TelemetryCache] Load failed: {e}")

    def _save(self):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ [TelemetryCache] Save failed: {e}")

    def get(self, text: str) -> Dict:
        return self.cache.get(text)

    def set(self, text: str, metrics: Dict):
        self.cache[text] = metrics
        # Auto-save on every write for persistence (MVP)
        self._save()
