"""
HandoffBuilder - 交接包建構器

負責在 AI session 切換時產生可驗證的交接包。
"""

import json
import hmac
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class DriftEntry:
    """偏移記錄"""

    timestamp: str
    choice: str
    toward: str
    away_from: str


@dataclass
class PendingTask:
    """未完成任務"""

    id: str
    description: str
    status: str  # "pending", "in_progress", "blocked"


@dataclass
class Phase:
    """當前相態（海洋意識論）"""

    current: str  # "雨", "雲", "霧", "雪", "潮", "漩", "冰", "化石"
    reason: str


@dataclass
class ContextSummary:
    """語場上下文摘要"""

    user_goal: str
    key_concepts: List[str]
    current_files: List[str]


@dataclass
class HandoffPacket:
    """交接包"""

    version: str
    timestamp: str
    source_model: str
    target_model: str
    phase: Phase
    pending_tasks: List[PendingTask]
    drift_log: List[DriftEntry]
    context_summary: ContextSummary
    signature: Optional[Dict[str, str]] = None


class HandoffBuilder:
    """交接包建構器"""

    VERSION = "1.0"

    def __init__(self, secret_key: Optional[str] = None):
        """
        初始化建構器

        Args:
            secret_key: HMAC 簽章密鑰。若未提供則從環境變數讀取。
        """
        self.secret_key = secret_key or self._load_secret()

    def _load_secret(self) -> str:
        """從環境或檔案載入密鑰"""
        import os

        return os.environ.get("HANDOFF_SECRET", "default_dev_secret")

    def build(
        self,
        source_model: str,
        target_model: str,
        phase: Phase,
        pending_tasks: List[PendingTask],
        drift_log: List[DriftEntry],
        context_summary: ContextSummary,
    ) -> HandoffPacket:
        """
        建構交接包

        Returns:
            HandoffPacket with computed signature
        """
        packet = HandoffPacket(
            version=self.VERSION,
            timestamp=datetime.utcnow().isoformat() + "Z",
            source_model=source_model,
            target_model=target_model,
            phase=phase,
            pending_tasks=pending_tasks,
            drift_log=drift_log,
            context_summary=context_summary,
        )

        # 計算簽章
        packet.signature = self._sign(packet)

        return packet

    def _sign(self, packet: HandoffPacket) -> Dict[str, str]:
        """計算 HMAC-SHA256 簽章"""
        # 移除 signature 欄位後序列化
        packet_dict = asdict(packet)
        packet_dict.pop("signature", None)

        # 正規化 JSON（確保一致的順序）
        canonical = json.dumps(packet_dict, sort_keys=True, ensure_ascii=False)

        # 計算 HMAC
        signature = hmac.new(
            self.secret_key.encode(), canonical.encode(), hashlib.sha256
        ).hexdigest()

        return {"algorithm": "HMAC-SHA256", "hash": signature}

    def verify(self, packet: HandoffPacket) -> bool:
        """驗證交接包簽章"""
        if not packet.signature:
            return False

        expected = self._sign(packet)
        return hmac.compare_digest(expected["hash"], packet.signature.get("hash", ""))

    def persist(self, packet: HandoffPacket, path: Optional[Path] = None) -> Path:
        """
        持久化交接包到檔案

        Args:
            packet: 要保存的交接包
            path: 保存路徑。預設為 memory/handoff/

        Returns:
            保存的檔案路徑
        """
        if path is None:
            path = Path("memory/handoff")

        path.mkdir(parents=True, exist_ok=True)

        filename = f"handoff_{packet.timestamp.replace(':', '-').replace('.', '-')}.json"
        filepath = path / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(asdict(packet), f, ensure_ascii=False, indent=2)

        return filepath

    def load(self, filepath: Path) -> HandoffPacket:
        """從檔案載入交接包"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        return HandoffPacket(
            version=data["version"],
            timestamp=data["timestamp"],
            source_model=data["source_model"],
            target_model=data["target_model"],
            phase=Phase(**data["phase"]),
            pending_tasks=[PendingTask(**t) for t in data["pending_tasks"]],
            drift_log=[DriftEntry(**d) for d in data["drift_log"]],
            context_summary=ContextSummary(**data["context_summary"]),
            signature=data.get("signature"),
        )


# 使用範例
if __name__ == "__main__":
    builder = HandoffBuilder()

    packet = builder.build(
        source_model="antigravity",
        target_model="codex",
        phase=Phase(current="霧", reason="多重未定的疊動"),
        pending_tasks=[
            PendingTask(id="task_001", description="完成調度器 MVP", status="in_progress")
        ],
        drift_log=[
            DriftEntry(
                timestamp="2026-02-04T09:07:00Z",
                choice="建立反思日誌而非直接改造電腦",
                toward="可反驗性",
                away_from="效率",
            )
        ],
        context_summary=ContextSummary(
            user_goal="設計 AI 治理框架",
            key_concepts=["生物學類比", "硬體層約束", "Isnād"],
            current_files=[
                "memory/antigravity_journal.md",
                "memory/external_framework_analysis/claw_governance_insight.md",
            ],
        ),
    )

    # 驗證
    print(f"Packet valid: {builder.verify(packet)}")

    # 持久化
    filepath = builder.persist(packet)
    print(f"Saved to: {filepath}")

    # 載入並再次驗證
    loaded = builder.load(filepath)
    print(f"Loaded packet valid: {builder.verify(loaded)}")
