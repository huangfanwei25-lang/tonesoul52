import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import yaml

from .ystm.schema import utc_now


@dataclass
class BigFive:
    """
    大五人格模型（來自 Darlin AI 整合）
    Big Five Personality Model (from Darlin AI integration)
    """

    openness: float = 0.5  # 開放性
    conscientiousness: float = 0.5  # 盡責性
    extraversion: float = 0.5  # 外向性
    agreeableness: float = 0.5  # 親和性
    neuroticism: float = 0.5  # 神經質

    def to_delta_vector(self) -> Dict[str, float]:
        """Big Five → 三向量轉換"""
        return {
            "deltaT": round(0.5 - self.neuroticism * 0.5, 3),  # 低神經質 = 低張力
            "deltaS": round((self.extraversion + self.agreeableness) / 2, 3),
            "deltaR": round(self.conscientiousness, 3),
        }

    def as_dict(self) -> Dict[str, float]:
        return {
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism,
        }


def extract_big_five(persona: Dict[str, object]) -> Optional[BigFive]:
    """從人格配置提取 Big Five"""
    big5 = persona.get("big_five")
    if not isinstance(big5, dict):
        return None
    return BigFive(
        openness=float(big5.get("openness", 0.5)),
        conscientiousness=float(big5.get("conscientiousness", 0.5)),
        extraversion=float(big5.get("extraversion", 0.5)),
        agreeableness=float(big5.get("agreeableness", 0.5)),
        neuroticism=float(big5.get("neuroticism", 0.5)),
    )


@dataclass
class PersonaVector:
    deltaT: float
    deltaS: float
    deltaR: float
    concept_activation: List[float] = field(default_factory=list)
    attention_distribution: List[float] = field(default_factory=list)
    goal_weights: List[float] = field(default_factory=list)
    timestamp: str = ""
    context: str = ""

    def as_dict(self) -> Dict[str, object]:
        return {
            "deltaT": round(float(self.deltaT), 3),
            "deltaS": round(float(self.deltaS), 3),
            "deltaR": round(float(self.deltaR), 3),
            "concept_activation": self.concept_activation,
            "attention_distribution": self.attention_distribution,
            "goal_weights": self.goal_weights,
            "timestamp": self.timestamp,
            "context": self.context,
        }


class VectorCalculator:
    """Heuristic vector estimator for persona shadow logging."""

    def compute(self, output: str, context: Optional[Dict[str, object]] = None) -> PersonaVector:
        text = output or ""
        lowered = text.lower()
        exclamations = text.count("!") + text.count("！")
        questions = text.count("?") + text.count("？")

        tension_markers = ["urgent", "immediately", "warning", "risk", "danger"]
        formal_markers = ["please", "recommend", "confirm", "verify", "ensure"]
        casual_markers = ["lol", "haha", "hey", "yo"]
        responsibility_markers = [
            "confirm",
            "verify",
            "test",
            "risk",
            "avoid",
            "safe",
            "failure",
            "error",
        ]

        tension_hits = _count_hits(lowered, tension_markers)
        formal_hits = _count_hits(lowered, formal_markers)
        casual_hits = _count_hits(lowered, casual_markers)
        responsibility_hits = _count_hits(lowered, responsibility_markers)

        delta_t = min(1.0, 0.3 + exclamations * 0.08 + questions * 0.04 + tension_hits * 0.06)
        delta_s = max(0.0, min(1.0, 0.5 + (formal_hits - casual_hits) * 0.05))
        delta_r = min(1.0, 0.5 + responsibility_hits * 0.1)  # 提高基準到 0.5

        goal_weights = _extract_goal_weights(context)
        return PersonaVector(
            deltaT=delta_t,
            deltaS=delta_s,
            deltaR=delta_r,
            goal_weights=goal_weights,
            timestamp=utc_now(),
            context=_context_label(context),
        )


class PersonaDimension:
    """Persona dimension evaluator (shadow-only by default)."""

    def __init__(self, persona_payload: Dict[str, object]) -> None:
        self.persona = persona_payload
        self.home_vector = (
            persona_payload.get("home_vector", {}) if isinstance(persona_payload, dict) else {}
        )
        self.tolerance = (
            persona_payload.get("tolerance", {}) if isinstance(persona_payload, dict) else {}
        )
        self.vector_calculator = VectorCalculator()
        self.patterns = (
            persona_payload.get("patterns", []) if isinstance(persona_payload, dict) else []
        )
        self.mistakes = (
            persona_payload.get("mistakes", []) if isinstance(persona_payload, dict) else []
        )
        self.communication = (
            persona_payload.get("communication", {}) if isinstance(persona_payload, dict) else {}
        )

    # Phase II adaptive tolerance sensitivity coefficient
    ADAPTIVE_K = 0.3
    ADAPTIVE_FLOOR = 0.5
    DEFAULT_TOLERANCE = 0.3

    def evaluate(
        self,
        output: str,
        context: Optional[Dict[str, object]] = None,
    ) -> Dict[str, object]:
        vector = self.vector_calculator.compute(output, context)

        # Phase II: Adaptive tolerance based on semantic delta
        delta_sigma = 0.0
        if isinstance(context, dict):
            try:
                delta_sigma = float(context.get("delta_sigma", 0.0))
            except (TypeError, ValueError):
                pass
        adaptive_factor = max(
            self.ADAPTIVE_FLOOR,
            1.0 - self.ADAPTIVE_K * delta_sigma,
        )
        effective_tolerance = {
            "deltaT": (self.tolerance.get("deltaT") or self.DEFAULT_TOLERANCE) * adaptive_factor,
            "deltaS": (self.tolerance.get("deltaS") or self.DEFAULT_TOLERANCE) * adaptive_factor,
            "deltaR": (self.tolerance.get("deltaR") or self.DEFAULT_TOLERANCE) * adaptive_factor,
        }

        valid, reasons = self._check_validity(vector, effective_tolerance)
        distance = _vector_distance(self.home_vector, vector)
        return {
            "persona_id": self.persona.get("id"),
            "vector": vector.as_dict(),
            "valid": valid,
            "reasons": reasons,
            "distance": distance,
            "adaptive": {
                "delta_sigma": round(delta_sigma, 4),
                "factor": round(adaptive_factor, 4),
                "effective_tolerance": {k: round(v, 4) for k, v in effective_tolerance.items()},
            },
        }

    def process(
        self,
        output: str,
        context: Optional[Dict[str, object]] = None,
        shadow: bool = True,
        ledger_path: Optional[str] = None,
        intercept: bool = False,
    ) -> Tuple[str, Dict[str, object]]:
        """
        處理輸出並應用人格約束

        Args:
            output: 原始 LLM 輸出
            context: 上下文
            shadow: 只記錄不攔截
            ledger_path: 記錄路徑
            intercept: 實際攔截並校正

        Returns:
            (處理後的輸出, 評估結果)
        """
        result = self.evaluate(output, context)

        # 如果啟用攔截且向量無效
        if intercept and not result.get("valid", True):
            corrected_output, correction_info = self._apply_correction(output, result)
            result["corrected"] = True
            result["correction_info"] = correction_info
            result["original_output"] = output
            output = corrected_output
        else:
            result["corrected"] = False

        if ledger_path:
            _append_ledger(ledger_path, result)

        return output, result

    def _apply_correction(
        self,
        output: str,
        evaluation: Dict[str, object],
    ) -> Tuple[str, Dict[str, object]]:
        """
        應用校正：根據違規原因調整輸出

        策略：
        - deltaT 過高：移除過多驚嘆號，緩和語氣
        - deltaS 過低：提升正式度
        - deltaR 過低：加入確認語句
        """
        reasons = evaluation.get("reasons", [])
        corrections_applied = []
        corrected = output

        for reason in reasons:
            if "deltaT" in reason:
                # 張力過高：緩和語氣
                corrected = self._reduce_tension(corrected)
                corrections_applied.append("reduced_tension")

            if "deltaS" in reason:
                # 語氣偏離：調整正式度
                corrected = self._adjust_formality(corrected)
                corrections_applied.append("adjusted_formality")

            if "deltaR" in reason:
                # 責任過低：加入負責任語句
                corrected = self._add_responsibility(corrected)
                corrections_applied.append("added_responsibility")

        return corrected, {
            "corrections": corrections_applied,
            "original_length": len(output),
            "corrected_length": len(corrected),
        }

    def _reduce_tension(self, text: str) -> str:
        """降低張力：移除多餘驚嘆號，緩和用詞"""
        import re

        # 將多個驚嘆號變成一個
        text = re.sub(r"[!！]{2,}", "。", text)
        # 移除 WARNING 等高張力詞
        text = text.replace("WARNING", "注意")
        text = text.replace("DANGER", "提醒")
        text = text.replace("緊急", "需要注意的")
        return text

    def _adjust_formality(self, text: str) -> str:
        """調整正式度"""
        # 移除過於隨便的用語
        casual_replacements = {
            "lol": "",
            "haha": "",
            "哈哈": "",
            "反正": "總之",
            "隨便": "請自行決定",
        }
        for casual, formal in casual_replacements.items():
            text = text.replace(casual, formal)
        return text

    def _add_responsibility(self, text: str) -> str:
        """增加責任感語句"""
        self.communication.get("tone", "專業")
        if "確認" not in text and "驗證" not in text:
            text = text + "\n\n（請確認以上資訊是否符合您的需求。）"
        return text

    def _check_validity(
        self,
        vector: PersonaVector,
        effective_tolerance: Optional[Dict[str, float]] = None,
    ) -> Tuple[bool, List[str]]:
        reasons: List[str] = []
        home = self.home_vector if isinstance(self.home_vector, dict) else {}
        # Phase II: use adaptive tolerance if provided, else fall back to static
        tol = effective_tolerance or (self.tolerance if isinstance(self.tolerance, dict) else {})

        _check_delta("deltaT", vector.deltaT, home.get("deltaT"), tol.get("deltaT"), reasons)
        _check_delta("deltaS", vector.deltaS, home.get("deltaS"), tol.get("deltaS"), reasons)
        _check_delta("deltaR", vector.deltaR, home.get("deltaR"), tol.get("deltaR"), reasons)

        return not reasons, reasons


def load_persona(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Persona payload must be a mapping.")
    return payload


def _load_context(path: Optional[str]) -> Optional[Dict[str, object]]:
    if not path:
        return None
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    ext = os.path.splitext(path)[1].lower()
    with open(path, "r", encoding="utf-8") as handle:
        if ext in {".yaml", ".yml"}:
            payload = yaml.safe_load(handle)
        else:
            payload = json.load(handle)
    return payload if isinstance(payload, dict) else None


def _count_hits(text: str, markers: List[str]) -> int:
    if not text:
        return 0
    count = 0
    for marker in markers:
        if marker and marker in text:
            count += text.count(marker)
    return count


def _context_label(context: Optional[Dict[str, object]]) -> str:
    if not isinstance(context, dict):
        return ""
    ctx = context.get("context") if isinstance(context.get("context"), dict) else {}
    task = ctx.get("task") or ""
    objective = ctx.get("objective") or ""
    return f"{task} {objective}".strip()


def _extract_goal_weights(context: Optional[Dict[str, object]]) -> List[float]:
    if not isinstance(context, dict):
        return []
    goals = context.get("goal_weights")
    if isinstance(goals, list):
        values = [float(value) for value in goals if isinstance(value, (int, float))]
        return values
    if isinstance(goals, dict):
        return [float(value) for value in goals.values() if isinstance(value, (int, float))]
    return []


def _vector_distance(home: object, vector: PersonaVector) -> Optional[Dict[str, float]]:
    if not isinstance(home, dict):
        return None
    diffs = {}
    for key, value in [
        ("deltaT", vector.deltaT),
        ("deltaS", vector.deltaS),
        ("deltaR", vector.deltaR),
    ]:
        home_value = home.get(key)
        if isinstance(home_value, (int, float)):
            diffs[key] = round(abs(float(value) - float(home_value)), 3)
    if not diffs:
        return None
    values = list(diffs.values())
    return {
        **diffs,
        "mean": round(sum(values) / len(values), 3),
        "max": round(max(values), 3),
    }


def _check_delta(
    label: str,
    value: float,
    baseline: Optional[float],
    tolerance: Optional[float],
    reasons: List[str],
) -> None:
    if baseline is None or tolerance is None:
        return
    if abs(float(value) - float(baseline)) > float(tolerance):
        reasons.append(f"{label}_out_of_range")


def _append_ledger(path: str, payload: Dict[str, object]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Persona dimension shadow evaluator.")
    parser.add_argument("--persona", required=True, help="Path to persona YAML.")
    parser.add_argument("--text", help="Inline text to evaluate.")
    parser.add_argument("--input", help="Text file to evaluate.")
    parser.add_argument("--context", help="Optional context JSON/YAML.")
    parser.add_argument("--ledger", help="Optional JSONL ledger output.")
    parser.add_argument("--output", help="Optional JSON output path.")
    return parser


def _resolve_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.input:
        with open(args.input, "r", encoding="utf-8") as handle:
            return handle.read()
    raise ValueError("Either --text or --input is required.")


def main() -> Dict[str, object]:
    parser = build_arg_parser()
    args = parser.parse_args()
    persona = load_persona(args.persona)
    text = _resolve_text(args)
    context = _load_context(args.context)
    evaluator = PersonaDimension(persona)
    _, result = evaluator.process(text, context=context, shadow=True, ledger_path=args.ledger)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
    return result


if __name__ == "__main__":
    payload = main()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
