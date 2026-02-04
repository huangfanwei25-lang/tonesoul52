"""
ToneSoul Simple Bridge
======================
Minimal Darlin-style HTTP bridge that prioritizes ToneSoul 5.2 output.
Uses stdlib only; falls back to raw Ollama if ToneSoul is unavailable.
"""

import json
import http.server
import socketserver
import threading
import urllib.request
import urllib.error
import math
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

ROOT = Path(__file__).resolve().parent
TS_ROOT = ROOT / "legacy" / "tonesoul-5.2"

if TS_ROOT.exists():
    sys.path.insert(0, str(TS_ROOT))

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("TS_MODEL", "gemma3:4b")
TONESOUL_PERSONA_ID = os.getenv("TONESOUL_PERSONA_ID", "darlin")
TONESOUL_ENABLE = os.getenv("TONESOUL_ENABLE", "1").lower() not in {"0", "false", "off", "no"}
MONITOR_ENABLE = os.getenv("MONITOR_ENABLE", "1").lower() not in {"0", "false", "off", "no"}
DRIFT_ENABLE = os.getenv("DRIFT_ENABLE", "1").lower() not in {"0", "false", "off", "no"}
MAX_HISTORY = int(os.getenv("BRIDGE_MAX_HISTORY", "8"))

DEFAULT_PROMPT = (
    "You are Xiaoyu, a warm and thoughtful companion.\n"
    "Keep replies short-to-medium, ask one brief clarifying question if needed.\n"
    "Avoid unsafe advice and do not overpromise.\n"
    "Respond in Traditional Chinese.\n"
)

PROMPT_PATH = os.getenv(
    "DARLIN_SYSTEM_PROMPT_PATH",
    str(ROOT / "legacy" / "darlin" / "解包" / "darlin_system_prompt.txt"),
)
PROMPT_INLINE = os.getenv("DARLIN_SYSTEM_PROMPT")

SERVICE_CODES = {
    "DarlinListening": "W001",
    "DarlinTTS": "W002",
    "DarlinSong": "W003",
    "DarlinAI": "W004",
    "DarlinEmpathy": "W005",
    "DarlinTranslate": "W006",
    "DarlinKnowledge": "W007",
    "DarlinMemory": "W008",
    "DarlinLogic": "W009",
    "postgresql-x64-17": "W010",
}

ACTION_INSTRUCTIONS = (
    "Return ONLY valid JSON with keys: reply, gesture, expression.\n"
    "reply: 1-3 sentences, Traditional Chinese.\n"
    "gesture: nod, shake, wave, bow, shrug, thinking, happy, none.\n"
    "expression: neutral, happy, angry, sad, relaxed, surprised.\n"
)

ALLOWED_GESTURES = {
    "nod",
    "shake",
    "wave",
    "bow",
    "shrug",
    "thinking",
    "happy",
    "none",
}
ALLOWED_EXPRESSIONS = {
    "neutral",
    "happy",
    "angry",
    "sad",
    "relaxed",
    "surprised",
}

MEMORY_ROOT = TS_ROOT / "memory" if TS_ROOT.exists() else ROOT / "memory"
LEDGER_PATH = MEMORY_ROOT / "conversation_ledger.jsonl"
LEDGER_LOCK = threading.Lock()

ToneSoulLLM = None
TONESOUL_AVAILABLE = False
TONESOUL_IMPORT_ERROR = None
if TS_ROOT.exists():
    try:
        from tonesoul52.tonesoul_llm import ToneSoulLLM

        TONESOUL_AVAILABLE = True
    except Exception as exc:
        TONESOUL_IMPORT_ERROR = str(exc)

_LLM_INSTANCE = None
_LLM_PERSONA_ID = None


def log(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)


def load_system_prompt() -> str:
    if PROMPT_INLINE:
        return PROMPT_INLINE
    if PROMPT_PATH and os.path.exists(PROMPT_PATH):
        try:
            with open(PROMPT_PATH, "r", encoding="utf-8") as handle:
                return handle.read().strip()
        except Exception as exc:
            log(f"Prompt read error: {exc}")
    return DEFAULT_PROMPT


def get_llm(persona_id: Optional[str] = None) -> Optional["ToneSoulLLM"]:
    global _LLM_INSTANCE, _LLM_PERSONA_ID
    if not (TONESOUL_ENABLE and TONESOUL_AVAILABLE):
        return None
    target_persona = persona_id or TONESOUL_PERSONA_ID
    if _LLM_INSTANCE is None or _LLM_PERSONA_ID != target_persona:
        _LLM_INSTANCE = ToneSoulLLM(
            persona_id=target_persona,
            model=DEFAULT_MODEL,
            base_path=TS_ROOT,
        )
        _LLM_PERSONA_ID = target_persona
    return _LLM_INSTANCE


def call_tonesoul(
    prompt: str,
    messages: Optional[List[Dict[str, Any]]] = None,
    persona_id: Optional[str] = None,
) -> Optional[str]:
    llm = get_llm(persona_id)
    if llm is None:
        return None

    system_prompt = load_system_prompt()
    try:
        if messages:
            has_system = any(m.get("role") == "system" for m in messages)
            if system_prompt and not has_system:
                messages = [{"role": "system", "content": system_prompt}] + messages
            output, _report = llm.chat(messages)
            return output
        output, _report = llm.generate(prompt, system=system_prompt)
        return output
    except Exception as exc:
        log(f"ToneSoul error: {exc}")
        return None


def call_ollama_generate(prompt: str, model: str = DEFAULT_MODEL) -> str:
    payload = {"model": model, "prompt": prompt, "stream": False}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("response", "")
    except Exception as exc:
        return f"Error: {exc}"


def call_ollama_chat(messages: List[Dict[str, Any]], model: str = DEFAULT_MODEL) -> str:
    payload = {"model": model, "messages": messages, "stream": False}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("message", {}).get("content", "")
    except Exception as exc:
        return f"Error: {exc}"


def get_ollama_embedding(text: str) -> list:
    payload = {"model": "nomic-embed-text", "prompt": text}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/embeddings",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("embedding", [])
    except Exception as exc:
        log(f"Embedding error: {exc}")
        return []


def _coerce_messages(raw: object) -> List[Dict[str, str]]:
    if not isinstance(raw, list):
        return []
    messages: List[Dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role not in ("user", "assistant", "system"):
            continue
        if not isinstance(content, str) or not content.strip():
            continue
        messages.append({"role": role, "content": content.strip()})
    return messages[-MAX_HISTORY:]


def _build_vrm_messages(user_message: str, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    system_prompt = load_system_prompt()
    action_prompt = f"{system_prompt}\n\n{ACTION_INSTRUCTIONS}".strip()
    messages = [{"role": "system", "content": action_prompt}]
    messages.extend(history)
    if user_message:
        if (
            not history
            or history[-1].get("role") != "user"
            or history[-1].get("content") != user_message
        ):
            messages.append({"role": "user", "content": user_message})
    return messages


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    candidate = text.strip()
    if candidate.startswith("{") and candidate.endswith("}"):
        try:
            payload = json.loads(candidate)
            return payload if isinstance(payload, dict) else None
        except json.JSONDecodeError:
            pass
    fenced = re.search(r"```json\\s*(\\{[\\s\\S]*?\\})\\s*```", candidate, re.IGNORECASE)
    if fenced:
        try:
            payload = json.loads(fenced.group(1))
            return payload if isinstance(payload, dict) else None
        except json.JSONDecodeError:
            pass
    first = candidate.find("{")
    last = candidate.rfind("}")
    if first != -1 and last != -1 and last > first:
        snippet = candidate[first : last + 1]
        try:
            payload = json.loads(snippet)
            return payload if isinstance(payload, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def _normalize_action(value: object, allowed: set[str]) -> Optional[str]:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    if normalized in {"none", "null", "nil", "n/a", "no"}:
        return None
    return normalized if normalized in allowed else None


def _parse_action_response(
    raw: str,
) -> tuple[str, Optional[str], Optional[str], Optional[Dict[str, Any]]]:
    payload = _extract_json(raw)
    if isinstance(payload, dict):
        reply = (
            payload.get("reply")
            or payload.get("response")
            or payload.get("content")
            or payload.get("text")
        )
        reply_text = reply.strip() if isinstance(reply, str) else ""
        gesture = _normalize_action(
            payload.get("gesture") or payload.get("action"), ALLOWED_GESTURES
        )
        expression = _normalize_action(
            payload.get("expression") or payload.get("emotion"), ALLOWED_EXPRESSIONS
        )
        return reply_text or raw.strip(), gesture, expression, payload
    return raw.strip(), None, None, None


def _cosine_similarity(a: List[float], b: List[float]) -> Optional[float]:
    if not a or not b or len(a) != len(b):
        return None
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for x, y in zip(a, b):
        dot += x * y
        norm_a += x * x
        norm_b += y * y
    if norm_a <= 0.0 or norm_b <= 0.0:
        return None
    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))


def _monitor_drift(user_message: str, reply_text: str) -> Dict[str, Any]:
    if not (MONITOR_ENABLE and DRIFT_ENABLE):
        return {}
    if not user_message or not reply_text:
        return {}
    emb_user = get_ollama_embedding(user_message)
    emb_reply = get_ollama_embedding(reply_text)
    similarity = _cosine_similarity(emb_user, emb_reply)
    if similarity is None:
        return {}
    return {
        "embedding_similarity": round(similarity, 4),
        "drift_score": round(1.0 - similarity, 4),
        "embedding_model": "nomic-embed-text",
    }


def _next_record_id() -> str:
    now = datetime.now()
    return now.strftime("%Y%m%d%H%M%S") + f"{int(now.microsecond / 1000):03d}"


def _log_conversation(
    user_message: str,
    reply_text: str,
    persona_id: str,
    gesture: Optional[str],
    expression: Optional[str],
    monitor: Dict[str, Any],
) -> None:
    if not MONITOR_ENABLE:
        return
    record = {
        "record_id": _next_record_id(),
        "timestamp": datetime.now().isoformat(),
        "type": "vrm_chat",
        "persona_id": persona_id,
        "context": {"user_message": user_message, "source": "vrm_viewer"},
        "response": reply_text,
        "status": "success",
        "actions": {"gesture": gesture, "expression": expression},
        "monitor": monitor,
        "meta": {
            "bridge": "tonesoul_simple",
            "tonesoul_enabled": bool(TONESOUL_ENABLE and TONESOUL_AVAILABLE),
            "model": DEFAULT_MODEL,
        },
    }
    try:
        LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LEDGER_LOCK:
            with LEDGER_PATH.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as exc:
        log(f"Ledger write error: {exc}")


class BridgeHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        log(f"[HTTP] {args[0]}")

    def send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        log(f"GET {self.path}")

        if self.path in ("/", "/status"):
            self.send_json(
                {
                    "status": "ok",
                    "bridge": "tonesoul_simple",
                    "tonesoul_enabled": TONESOUL_ENABLE,
                    "tonesoul_available": TONESOUL_AVAILABLE,
                    "tonesoul_persona": TONESOUL_PERSONA_ID,
                    "tonesoul_error": TONESOUL_IMPORT_ERROR,
                    "services": {name: "running" for name in SERVICE_CODES.keys()},
                }
            )
            return

        if self.path.startswith("/service/"):
            service_name = self.path.split("/service/")[1]
            self.send_json(
                {
                    "service": service_name,
                    "status": "running",
                    "code": SERVICE_CODES.get(service_name, "W000"),
                }
            )
            return

        self.send_json({"error": "Unknown endpoint", "path": self.path}, 404)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else ""

        log(f"POST {self.path}")
        if body:
            try:
                data = json.loads(body)
            except Exception:
                data = {}
        else:
            data = {}

        persona_id = (
            data.get("persona") if isinstance(data.get("persona"), str) else TONESOUL_PERSONA_ID
        )

        if "vrm" in self.path.lower():
            raw_message = data.get("message", data.get("text", data.get("prompt", "")))
            message = raw_message.strip() if isinstance(raw_message, str) else ""
            history = _coerce_messages(data.get("messages") or data.get("history") or [])
            if not message and not history:
                self.send_json({"error": "No prompt provided"}, 400)
                return
            messages = _build_vrm_messages(message, history)
            response = call_tonesoul("", messages=messages, persona_id=persona_id)
            if response is None:
                response = call_ollama_chat(messages)
            reply_text, gesture, expression, _payload = _parse_action_response(response or "")
            monitor = _monitor_drift(message, reply_text)
            _log_conversation(message, reply_text, persona_id, gesture, expression, monitor)
            self.send_json(
                {
                    "status": "ok",
                    "response": reply_text,
                    "gesture": gesture,
                    "expression": expression,
                    "monitor": monitor,
                }
            )
            return

        if any(key in self.path.lower() for key in ("ai", "chat", "generate")):
            messages = data.get("messages")
            prompt = data.get("prompt", data.get("message", data.get("text", "")))

            response = None
            if isinstance(messages, list):
                response = call_tonesoul("", messages=messages, persona_id=persona_id)
                if response is None:
                    response = call_ollama_chat(messages)
            elif prompt:
                response = call_tonesoul(prompt, persona_id=persona_id)
                if response is None:
                    response = call_ollama_generate(prompt)

            if response:
                self.send_json({"response": response, "status": "ok"})
            else:
                self.send_json({"error": "No prompt provided"}, 400)
            return

        if "embed" in self.path.lower() or "translate" in self.path.lower():
            text = data.get("text", data.get("input", ""))
            if text:
                embedding = get_ollama_embedding(text)
                self.send_json({"embedding": embedding, "status": "ok"})
            else:
                self.send_json({"error": "No text provided"}, 400)
            return

        if "service" in self.path.lower():
            self.send_json({"status": "ok", "message": "Service operation mocked"})
            return

        self.send_json({"status": "ok", "message": "Mocked response"})


def run_server_on_port(port: int) -> None:
    try:
        socketserver.TCPServer.allow_reuse_address = True
        server = socketserver.ThreadingTCPServer(("", port), BridgeHandler)
        log(f"Listening on port {port}")
        server.serve_forever()
    except OSError as exc:
        log(f"Port {port} failed: {exc}")


def parse_ports() -> List[int]:
    raw = os.getenv("BRIDGE_PORTS", "8080,9000,5000,3000,13579,8000")
    ports = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            ports.append(int(token))
        except ValueError:
            log(f"Ignoring invalid port: {token}")
    return ports


def run_server() -> None:
    ports = parse_ports()
    log("=" * 50)
    log("ToneSoul Simple Bridge Started")
    log(f"Ollama backend: {OLLAMA_URL}")
    log(f"Default model: {DEFAULT_MODEL}")
    if TONESOUL_ENABLE and TONESOUL_AVAILABLE:
        log(f"ToneSoul: enabled (persona={TONESOUL_PERSONA_ID})")
    elif not TONESOUL_ENABLE:
        log("ToneSoul: disabled via TONESOUL_ENABLE")
    elif TONESOUL_IMPORT_ERROR:
        log(f"ToneSoul: import failed ({TONESOUL_IMPORT_ERROR})")
    else:
        log(f"ToneSoul: unavailable (missing {TS_ROOT})")
    log(f"Monitor: {'on' if MONITOR_ENABLE else 'off'} (drift={'on' if DRIFT_ENABLE else 'off'})")
    log(f"Ports: {ports}")
    log("=" * 50)

    threads = []
    for port in ports:
        t = threading.Thread(target=run_server_on_port, args=(port,), daemon=True)
        t.start()
        threads.append(t)

    log("Waiting for Darlin-compatible connections...")
    try:
        while True:
            import time

            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run_server()
