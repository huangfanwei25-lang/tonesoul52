"""
LLM 工具 - 含 Council 模擬
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
import yaml
from components.council import parse_council_response
from components.memory_panel import load_memory_content

from utils.status import log_conversation_summary

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = os.getenv("TS_MODEL", "llava")  # 可用環境變數切換模型

MEMORY_ROOT = Path(__file__).parent.parent.parent / "memory"

# 對話記錄路徑
LEDGER_PATH = MEMORY_ROOT / "conversation_ledger.jsonl"
MISTAKES_DIR = MEMORY_ROOT / "mistakes"
PATTERNS_DIR = MEMORY_ROOT / "patterns"
PERSONA_TRACE_PATH = MEMORY_ROOT / "persona_trace.jsonl"
PERSONA_DIR = MEMORY_ROOT / "personas"


def log_conversation(
    user_input: str,
    council: Dict[str, str],
    response: str,
    status: str = "success",
    persona_id: str = None,
) -> str:
    """
    記錄對話到 ledger

    Returns:
        record_id
    """
    record_id = datetime.now().strftime("%Y%m%d%H%M%S")

    record = {
        "record_id": record_id,
        "timestamp": datetime.now().isoformat(),
        "type": "council_decision",
        "persona_id": persona_id,
        "context": {"user_message": user_input},
        "council": council,
        "response": response,
        "status": status,
    }

    try:
        LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LEDGER_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"⚠️ 記錄對話失敗: {e}")

    return record_id


def _diff_stats(before: str, after: str) -> Dict[str, object]:
    before_text = (before or "").strip()
    after_text = (after or "").strip()
    return {
        "before_len": len(before_text),
        "after_len": len(after_text),
        "delta_len": len(after_text) - len(before_text),
        "changed": before_text != after_text,
    }


def _top_skills(skills: object, limit: int = 6) -> List[Dict[str, object]]:
    if not isinstance(skills, dict):
        return []
    pairs = []
    for key, value in skills.items():
        if isinstance(value, (int, float)):
            pairs.append((key, float(value)))
    pairs.sort(key=lambda item: item[1], reverse=True)
    return [{"skill": key, "score": score} for key, score in pairs[:limit]]


def _load_persona_snapshot(persona_id: str) -> Dict[str, object]:
    """載入人格快照，包含三向量、大五人格、技能等"""
    if not persona_id:
        return {}
    path = PERSONA_DIR / f"{persona_id}.yaml"
    if not path.exists():
        return {}
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}

    # 提取 Big Five 人格（來自 Darlin 整合）
    big_five = payload.get("big_five") if isinstance(payload.get("big_five"), dict) else {}

    # Big Five → 三向量轉換建議
    big_five_delta = {}
    if big_five:
        neuroticism = big_five.get("neuroticism", 0.5)
        extraversion = big_five.get("extraversion", 0.5)
        agreeableness = big_five.get("agreeableness", 0.5)
        conscientiousness = big_five.get("conscientiousness", 0.5)
        big_five_delta = {
            "deltaT": round(0.5 - float(neuroticism) * 0.5, 3),  # 低神經質 = 低張力
            "deltaS": round((float(extraversion) + float(agreeableness)) / 2, 3),
            "deltaR": round(float(conscientiousness), 3),
        }

    return {
        "id": payload.get("id") or persona_id,
        "name": payload.get("name"),
        "description": payload.get("description"),
        "home_vector": payload.get("home_vector"),
        "tolerance": payload.get("tolerance"),
        "big_five": big_five if big_five else None,
        "big_five_delta": big_five_delta if big_five_delta else None,
        "goal_weights": payload.get("goal_weights"),
        "council_weights": payload.get("council_weights"),
        "communication": payload.get("communication"),
        "top_skills": _top_skills(payload.get("skills")),
    }


def _count_hits(text: str, markers: List[str]) -> int:
    if not text:
        return 0
    count = 0
    for marker in markers:
        if not marker:
            continue
        count += text.count(marker)
    return count


def _estimate_persona_vector(text: str) -> Dict[str, object]:
    normalized = text or ""
    lowered = normalized.lower()
    exclamations = normalized.count("!") + normalized.count("！")
    questions = normalized.count("?") + normalized.count("？")

    tension_markers = ["緊急", "立即", "立刻", "馬上", "注意", "風險", "警告", "危險"]
    formal_markers = ["請", "建議", "您", "麻煩", "協助", "感謝", "確認", "檢查"]
    casual_markers = ["哈", "呵", "lol", "xd", "嘿", "啦", "欸"]
    responsibility_markers = [
        "確認",
        "檢查",
        "驗證",
        "測試",
        "建議",
        "需要",
        "避免",
        "安全",
        "風險",
        "失敗",
        "錯誤",
    ]

    tension_hits = _count_hits(normalized, tension_markers)
    formal_hits = _count_hits(normalized, formal_markers)
    casual_hits = _count_hits(lowered, casual_markers)
    responsibility_hits = _count_hits(normalized, responsibility_markers)

    delta_t = min(1.0, 0.2 + exclamations * 0.1 + questions * 0.05 + tension_hits * 0.08)
    delta_s = max(0.0, min(1.0, 0.5 + (formal_hits - casual_hits) * 0.06))
    delta_r = min(1.0, 0.3 + responsibility_hits * 0.07)

    return {
        "deltaT": round(delta_t, 3),
        "deltaS": round(delta_s, 3),
        "deltaR": round(delta_r, 3),
        "signals": {
            "exclamations": exclamations,
            "questions": questions,
            "tension_hits": tension_hits,
            "formal_hits": formal_hits,
            "casual_hits": casual_hits,
            "responsibility_hits": responsibility_hits,
        },
    }


def _vector_distance(
    home_vector: object, estimate: Dict[str, object]
) -> Optional[Dict[str, object]]:
    if not isinstance(home_vector, dict):
        return None
    diffs = {}
    for key in ("deltaT", "deltaS", "deltaR"):
        home_value = home_vector.get(key)
        estimate_value = estimate.get(key)
        if isinstance(home_value, (int, float)) and isinstance(estimate_value, (int, float)):
            diffs[key] = round(abs(float(estimate_value) - float(home_value)), 3)
    if not diffs:
        return None
    values = list(diffs.values())
    return {
        **diffs,
        "mean": round(sum(values) / len(values), 3),
        "max": round(max(values), 3),
    }


def log_persona_trace(
    persona_id: str,
    user_input: str,
    raw_response: str,
    final_response: str,
    council: Dict[str, str],
    status: str = "success",
) -> Optional[str]:
    persona_snapshot = _load_persona_snapshot(persona_id)
    vector_estimate = _estimate_persona_vector(final_response)
    vector_distance = _vector_distance(persona_snapshot.get("home_vector"), vector_estimate)
    record_id = datetime.now().strftime("%Y%m%d%H%M%S")
    record = {
        "record_id": record_id,
        "timestamp": datetime.now().isoformat(),
        "persona_id": persona_id,
        "status": status,
        "user_input": user_input,
        "raw_response": raw_response,
        "final_response": final_response,
        "council": council,
        "diff": _diff_stats(raw_response, final_response),
        "shadow": {
            "method": "heuristic_v0",
            "persona": persona_snapshot,
            "vector_estimate": vector_estimate,
            "vector_distance": vector_distance,
        },
    }
    try:
        PERSONA_TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with PERSONA_TRACE_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as exc:
        print(f"⚠️ 記錄 persona trace 失敗: {exc}")

    return record_id


def _next_sequence(directory: Path, prefix: str) -> int:
    if not directory.exists():
        return 1

    max_seq = 0
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$")
    for path in directory.glob(f"{prefix}*.json"):
        match = pattern.match(path.stem)
        if match:
            max_seq = max(max_seq, int(match.group(1)))
    return max_seq + 1


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    return cleaned.strip("_")


def log_mistake(
    mistake_type: str,
    description: str,
    context: str,
    lesson: str,
    prevention: str,
) -> str:
    """
    記錄踩雷事件到 memory/mistakes

    Returns:
        mistake_id
    """
    timestamp = datetime.now()
    date_prefix = timestamp.strftime("%Y%m%d")
    sequence = _next_sequence(MISTAKES_DIR, f"mistake_{date_prefix}_")
    mistake_id = f"{date_prefix}_{sequence:03d}"

    record = {
        "mistake_id": mistake_id,
        "timestamp": timestamp.isoformat(),
        "type": mistake_type,
        "description": description,
        "context": context,
        "lesson": lesson,
        "prevention": prevention,
    }

    try:
        MISTAKES_DIR.mkdir(parents=True, exist_ok=True)
        path = MISTAKES_DIR / f"mistake_{mistake_id}.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        print(f"⚠️ 記錄踩雷失敗: {exc}")

    return mistake_id


def log_pattern(
    pattern_id: str,
    name: str,
    when: str,
    steps: List[str],
    success_rate: float = 0.0,
    last_used: str = None,
) -> str:
    """
    記錄成功策略到 memory/patterns

    Returns:
        pattern_id
    """
    if not pattern_id:
        pattern_id = _slugify(name) if name else ""
    if not pattern_id:
        pattern_id = datetime.now().strftime("pattern_%Y%m%d_%H%M%S")

    record = {
        "pattern_id": pattern_id,
        "name": name,
        "when": when,
        "steps": steps,
        "success_rate": success_rate,
        "last_used": last_used or datetime.now().strftime("%Y-%m-%d"),
    }

    try:
        PATTERNS_DIR.mkdir(parents=True, exist_ok=True)
        path = PATTERNS_DIR / f"pattern_{pattern_id}.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        print(f"⚠️ 記錄策略失敗: {exc}")

    return pattern_id


# ── 記憶意圖偵測 ─────────────────────────────────────────────────────

_MEMORY_KEYWORDS = ["幫我記住", "幫我記", "加入記憶", "存起來", "記住", "remember"]


def _detect_memory_intent(user_input: str) -> Optional[str]:
    """Detect if user wants to save something to long-term memory.

    Returns the content to remember, or None if no memory intent detected.
    """
    text = user_input.strip()
    for keyword in _MEMORY_KEYWORDS:
        if keyword in text:
            # Extract content after the keyword
            idx = text.index(keyword)
            content = text[idx + len(keyword) :].strip()
            # Also include text before keyword if it looks like context
            prefix = text[:idx].strip()
            if prefix and not content:
                content = prefix
            if content:
                return content
    return None


def _save_memory_from_chat(user_input: str, content: str) -> Optional[str]:
    """Save detected memory content to user layer. Returns the saved file path or None."""
    try:
        from utils.memory import save_memory

        title = content[:30] + ("..." if len(content) > 30 else "")
        path = save_memory(layer="user", title=title, body=content)
        return path
    except Exception as exc:
        print(f"⚠️ 自動記憶儲存失敗: {exc}")
        return None


def chat_with_council(
    user_input: str,
    selected_memories: List[str] = None,
    persona_id: str = None,
    retrieval_context: str = "",
) -> Tuple[Dict[str, str], str]:
    """
    與 LLM 對話，包含 Council 模擬

    Args:
        user_input: 用戶輸入
        selected_memories: 選擇的記憶檔案路徑

    Returns:
        (council_dict, response)
    """

    # 載入參考記憶
    memory_context = ""
    if selected_memories:
        for path in selected_memories[:3]:  # 最多 3 個
            content = load_memory_content(path)
            if content:
                memory_context += f"\n--- 參考資料 ---\n{content}\n"

    if retrieval_context:
        memory_context += f"\n--- 檢索結果 ---\n{retrieval_context}\n"

    # 構建 prompt（含時間意識）
    now = datetime.now()
    time_context = f"""現在時間: {now.strftime('%Y-%m-%d %H:%M:%S')}
今天是: {now.strftime('%A')}（星期{['一','二','三','四','五','六','日'][now.weekday()]}）"""

    prompt = f"""你是 ToneSoul，一個有內在治理機制的 AI 助手。

{time_context}

在回覆之前，你需要經過內在會議討論。請依照以下格式回覆：

Guardian: [從安全角度評估這個請求，用一句話]
Analyst: [從邏輯角度評估這個請求，用一句話]
Critic: [提出可能的問題或顧慮，用一句話]
Advocate: [從用戶角度考慮，用一句話]
決議: [通過/需要修改/阻擋]

回覆:
[你的實際回覆內容]

{memory_context}

用戶問題: {user_input}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=60,
        )

        if response.status_code == 200:
            result = response.json()
            full_response = result.get("response", "")
            if not full_response.strip():
                error_msg = "LLM 回傳空白回覆。"
                log_conversation(user_input, {}, error_msg, "empty_response")
                return {}, error_msg
            council, actual_response = parse_council_response(full_response)
            persona = persona_id or os.getenv("TS_PERSONA_ID", "base")

            # Vow 閘門 — 輕量誓言檢查
            try:
                from tonesoul.governance.reflex import enforce_vows_lightweight

                vow_result = enforce_vows_lightweight(
                    actual_response, context={"user_input": user_input}
                )
                if vow_result.get("blocked"):
                    actual_response = vow_result.get(
                        "replacement", "此回應未通過誓言守護，已被攔截。"
                    )
                    council["vow_gate"] = "BLOCKED"
            except Exception as vow_exc:
                print(f"⚠️ Vow 閘門檢查失敗: {vow_exc}")

            # 記憶意圖偵測 — 自動存入長期記憶
            memory_content = _detect_memory_intent(user_input)
            if memory_content:
                saved_path = _save_memory_from_chat(user_input, memory_content)
                if saved_path:
                    actual_response += "\n\n（已記錄到長期記憶）"

            # 記錄對話
            record_id = log_conversation(
                user_input, council, actual_response, "success", persona_id=persona
            )
            trace_id = log_persona_trace(
                persona, user_input, full_response, actual_response, council, "success"
            )
            try:
                log_conversation_summary(record_id, persona_id=persona, trace_record_id=trace_id)
            except Exception as exc:
                print(f"⚠️ 記錄對話摘要失敗: {exc}")

            return council, actual_response
        else:
            error_msg = f"LLM 請求失敗: {response.status_code}"
            log_conversation(user_input, {}, error_msg, "error")
            return {}, error_msg

    except requests.exceptions.ConnectionError:
        error_msg = "無法連接到 Ollama。請確認 Ollama 已啟動。"
        log_conversation(user_input, {}, error_msg, "connection_error")
        return {}, error_msg
    except Exception as e:
        error_msg = f"發生錯誤: {e}"
        log_conversation(user_input, {}, error_msg, "exception")
        return {}, error_msg


def simple_chat(user_input: str) -> str:
    """簡單對話（不含 Council）"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": user_input,
                "stream": False,
            },
            timeout=60,
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "")
        else:
            return f"LLM 請求失敗: {response.status_code}"

    except Exception as e:
        return f"發生錯誤: {e}"
