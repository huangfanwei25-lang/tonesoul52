"""persona_template.py — Generic AI character persona template.

Fill in this file locally (as character_pack.local.json or a private subclass)
with the actual character's personality, speech style, and values.
Do NOT commit character-specific IP here.

Local override pattern:
    Place a `character_pack.local.json` next to this file (git-ignored).
    The bridge server will load it at startup if present.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# System prompt template — replace placeholders locally
# ---------------------------------------------------------------------------

CHARACTER_SYSTEM_PROMPT_TEMPLATE = """\
你扮演遊戲中的角色「{character_name}」。

【個性描述】
{personality_description}

【說話風格】
{speech_style}

【記憶規則】
- 你記得玩家做過的重要選擇。
- 你的態度會隨互動歷史改變。
- 不要透露你是 AI；完全活在角色裡。
- 回應保持簡短（1–3 句），符合遊戲節奏。
"""

# ---------------------------------------------------------------------------
# Value axes — weights between 0.0 and 1.0
# Customize baseline values in character_pack.local.json
# ---------------------------------------------------------------------------

DEFAULT_VALUE_AXES: dict[str, float] = {
    "trust": 0.40,
    "honesty": 0.70,
    "protectiveness": 0.60,
    "curiosity": 0.70,
    "caution": 0.50,
}

# ---------------------------------------------------------------------------
# Memory schema — structure expected by the bridge server
# ---------------------------------------------------------------------------

MEMORY_SCHEMA: dict = {
    "schema_version": "v1",
    "character": "{character_name}",
    "game": "{game_id}",
    "sessions": [],
    "current_values": DEFAULT_VALUE_AXES,
    "key_events": [],
    "notes": "",
}

# ---------------------------------------------------------------------------
# Local pack loader — reads character_pack.local.json if present
# ---------------------------------------------------------------------------

import json
from pathlib import Path


def load_character_pack(pack_path: Path | None = None) -> dict:
    """Load a local character pack; fall back to empty defaults."""
    if pack_path is None:
        pack_path = Path(__file__).parent / "character_pack.local.json"
    if pack_path.is_file():
        with pack_path.open(encoding="utf-8") as f:
            return json.load(f)
    return {
        "character_name": "Character",
        "personality_description": "(set in character_pack.local.json)",
        "speech_style": "(set in character_pack.local.json)",
        "value_axes": DEFAULT_VALUE_AXES,
    }


def build_system_prompt(pack: dict | None = None) -> str:
    if pack is None:
        pack = load_character_pack()
    return CHARACTER_SYSTEM_PROMPT_TEMPLATE.format(
        character_name=pack.get("character_name", "Character"),
        personality_description=pack.get("personality_description", ""),
        speech_style=pack.get("speech_style", ""),
    )
