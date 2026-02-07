"""
ToneSoul 持久化
ToneSoul Persistence Layer

保存和載入：
- Session 歷史
- 校正記憶
- 品質報告
- 長期趨勢
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class ToneSoulPersistence:
    """
    ToneSoul 持久化層

    使用 JSONL 格式保存資料
    """

    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path(__file__).parent.parent / "memory"

        # 檔案路徑
        self.sessions_path = self.base_path / "tonesoul_sessions.jsonl"
        self.corrections_path = self.base_path / "tonesoul_corrections.jsonl"
        self.quality_path = self.base_path / "tonesoul_quality.jsonl"

    def save_session(self, session_data: Dict) -> str:
        """保存 session 資料"""
        session_id = datetime.now().strftime("%Y%m%d%H%M%S")

        record = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            **session_data,
        }

        self._append_jsonl(self.sessions_path, record)
        return session_id

    def save_correction(self, correction: Dict) -> None:
        """保存校正記憶"""
        record = {
            "timestamp": datetime.now().isoformat(),
            **correction,
        }
        self._append_jsonl(self.corrections_path, record)

    def save_quality_snapshot(self, quality: Dict) -> None:
        """保存品質快照"""
        record = {
            "timestamp": datetime.now().isoformat(),
            **quality,
        }
        self._append_jsonl(self.quality_path, record)

    def load_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """載入最近的 sessions"""
        return self._read_jsonl(self.sessions_path, limit)

    def load_corrections(self, limit: int = 50) -> List[Dict]:
        """載入校正記憶"""
        return self._read_jsonl(self.corrections_path, limit)

    def load_quality_history(self, limit: int = 30) -> List[Dict]:
        """載入品質歷史"""
        return self._read_jsonl(self.quality_path, limit)

    def get_statistics(self) -> Dict:
        """取得統計資訊"""
        sessions = self._read_jsonl(self.sessions_path)
        corrections = self._read_jsonl(self.corrections_path)
        quality = self._read_jsonl(self.quality_path)

        return {
            "total_sessions": len(sessions),
            "total_corrections": len(corrections),
            "quality_snapshots": len(quality),
            "last_session": sessions[-1] if sessions else None,
            "last_quality": quality[-1] if quality else None,
        }

    def _append_jsonl(self, path: Path, record: Dict) -> None:
        """附加記錄到 JSONL 檔案"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _read_jsonl(self, path: Path, limit: int = None) -> List[Dict]:
        """讀取 JSONL 檔案"""
        if not path.exists():
            return []

        records = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        if limit:
            return records[-limit:]
        return records


def create_persistence(persona_id: str = "antigravity") -> ToneSoulPersistence:
    """創建持久化實例"""
    base_path = Path(__file__).parent.parent / "memory" / "tonesoul" / persona_id
    return ToneSoulPersistence(base_path=base_path)


# === 整合到 UnifiedCore ===


class PersistentCore:
    """
    帶持久化的 UnifiedCore

    自動保存 session 和校正記憶
    """

    def __init__(self, core, persona_id: str = "antigravity"):
        self.core = core
        self.persona_id = persona_id
        self.persistence = create_persistence(persona_id)

    def process(self, output: str, **kwargs):
        """處理並自動保存校正"""
        result_output, report = self.core.process(output, **kwargs)

        # 如果有校正，保存
        if report.get("correction"):
            self.persistence.save_correction(
                {
                    "original_output": output,
                    "corrected_output": result_output,
                    "correction_info": report.get("correction"),
                    "vector": report.get("output_vector"),
                    "zone": report.get("semantic_tension", {}).get("zone"),
                }
            )

        return result_output, report

    def end_session(self):
        """結束 session 並保存"""
        session_report = self.core.end_session()

        # 保存 session
        session_id = self.persistence.save_session(
            {
                "persona_id": self.persona_id,
                "summary": session_report.get("session_summary"),
                "long_term": session_report.get("long_term_trend"),
                "alerts": session_report.get("alerts"),
            }
        )

        # 保存品質快照
        if session_report.get("session_summary"):
            self.persistence.save_quality_snapshot(session_report["session_summary"])

        return {
            **session_report,
            "session_id": session_id,
        }

    def get_history_summary(self) -> Dict:
        """取得歷史摘要"""
        return self.persistence.get_statistics()


# === 測試 ===
if __name__ == "__main__":
    print("=" * 60)
    print("   ToneSoul 持久化層測試")
    print("=" * 60)

    persistence = create_persistence("antigravity")

    print(f"\n📁 儲存路徑: {persistence.base_path}")

    # 模擬保存
    print("\n💾 模擬保存...")

    # 保存 session
    session_id = persistence.save_session(
        {
            "persona_id": "antigravity",
            "turns": 5,
            "avg_delta_s": 0.18,
            "intervention_rate": 0.0,
        }
    )
    print(f"  ✅ Session saved: {session_id}")

    # 保存 correction
    persistence.save_correction(
        {
            "original_output": "這絕對是對的！！！",
            "corrected_output": "這應該是對的，但請確認。",
            "reason": "reduced_tension",
        }
    )
    print("  ✅ Correction saved")

    # 保存 quality
    persistence.save_quality_snapshot(
        {
            "avg_delta_s": 0.18,
            "contract_pass_rate": 0.9,
            "trend": "stable",
        }
    )
    print("  ✅ Quality snapshot saved")

    # 讀取統計
    print("\n📊 統計:")
    stats = persistence.get_statistics()
    print(f"  Sessions: {stats['total_sessions']}")
    print(f"  Corrections: {stats['total_corrections']}")
    print(f"  Quality snapshots: {stats['quality_snapshots']}")

    print("\n" + "=" * 60)
    print("   測試完成")
    print("=" * 60)
