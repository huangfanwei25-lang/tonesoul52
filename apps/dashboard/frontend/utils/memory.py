"""
記憶操作工具
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

MEMORY_LAYERS = ("seeds", "user", "session", "agent")
CONVERSATION_LEDGER = "conversation_ledger.jsonl"


def get_workspace_root() -> Path:
    """取得工作區根目錄"""
    return Path(__file__).parent.parent.parent


def list_memory_entries(layers: Optional[List[str]] = None) -> List[Dict]:
    """列出記憶內容（支援多層記憶）"""

    workspace = get_workspace_root()
    layers = layers or list(MEMORY_LAYERS)

    entries: List[Dict] = []
    for layer in layers:
        layer_dir = workspace / "memory" / layer
        if not layer_dir.exists():
            continue
        for seed_path in layer_dir.glob("*.json"):
            try:
                with open(seed_path, "r", encoding="utf-8") as f:
                    seed = json.load(f)
                entries.append(
                    {
                        "path": str(seed_path),
                        "id": seed.get("run_id", seed_path.stem),
                        "title": seed.get("content", {}).get("title", "未命名"),
                        "gate": seed.get("gate_overall", "unknown"),
                        "time": seed_path.stat().st_mtime,
                        "layer": layer,
                    }
                )
            except Exception:
                continue

    return sorted(entries, key=lambda x: x["time"], reverse=True)


def list_seeds() -> List[Dict]:
    """列出所有種子記憶"""

    return list_memory_entries(layers=["seeds"])


def list_skills() -> List[Dict]:
    """列出所有技能"""

    workspace = get_workspace_root()
    skills_dir = workspace / "spec" / "skills"

    skills = []
    if skills_dir.exists():
        for skill_path in skills_dir.glob("*.yaml"):
            skills.append(
                {
                    "path": str(skill_path),
                    "name": skill_path.stem.replace("_", " ").title(),
                }
            )

    return skills


def list_conversations(limit: int = 20) -> List[Dict]:
    """列出對話記錄（conversation ledger）"""

    workspace = get_workspace_root()
    ledger_path = workspace / "memory" / CONVERSATION_LEDGER
    if not ledger_path.exists():
        return []

    entries: List[Dict] = []
    try:
        with ledger_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(payload, dict):
                    continue
                record_id = payload.get("record_id") or ""
                context = payload.get("context") if isinstance(payload.get("context"), dict) else {}
                user_message = (
                    context.get("user_message") or payload.get("user_message") or "未命名對話"
                )
                timestamp = payload.get("timestamp")
                time_value = _parse_iso_time(timestamp) or ledger_path.stat().st_mtime
                entries.append(
                    {
                        "path": f"ledger:{record_id}",
                        "id": record_id or user_message,
                        "title": user_message,
                        "time": time_value,
                        "layer": "conversation",
                    }
                )
    except Exception:
        return []

    entries = sorted(entries, key=lambda x: x["time"], reverse=True)
    return entries[:limit]


def load_conversation_entry(record_id: str) -> Optional[Dict]:
    """載入特定對話記錄"""

    if not record_id:
        return None
    workspace = get_workspace_root()
    ledger_path = workspace / "memory" / CONVERSATION_LEDGER
    if not ledger_path.exists():
        return None
    try:
        with ledger_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, dict) and payload.get("record_id") == record_id:
                    return payload
    except Exception:
        return None
    return None


def save_memory(content: str, title: str = None, layer: str = "seeds") -> str:
    """儲存新記憶"""

    workspace = get_workspace_root()
    if layer not in MEMORY_LAYERS:
        layer = "seeds"
    memory_dir = workspace / "memory" / layer
    memory_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    memory_id = f"manual_{timestamp}"

    memory = {
        "seed_version": "0.1",
        "run_id": memory_id,
        "layer": layer,
        "content": {
            "title": title or f"手動記憶 {timestamp}",
            "body": content,
        },
        "source": "manual",
        "created_at": datetime.now().isoformat(),
    }

    path = memory_dir / f"{memory_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

    return str(path)


def load_memory(path: str) -> Optional[Dict]:
    """載入記憶"""

    path = Path(path)
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return None


def _parse_iso_time(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None
