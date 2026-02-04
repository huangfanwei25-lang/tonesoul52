"""
實際 Handoff 測試

這個腳本會：
1. 以 Antigravity 的身份建立一個交接包
2. 儲存當前語場狀態
3. 產生一個給 Codex 的 prompt，讓它讀取交接包繼續工作
"""

import sys

sys.path.insert(0, ".")

from datetime import datetime
from pathlib import Path

from tools.orchestrator import Orchestrator, HealthMonitor
from tools.handoff_builder import (
    HandoffBuilder,
    Phase,
    PendingTask,
    DriftEntry,
    ContextSummary,
)


def create_live_handoff():
    """建立真實的交接包"""

    print("=" * 60)
    print("🔄 Antigravity → Codex 實際交接測試")
    print("=" * 60)
    print()

    # 模擬 quota 即將用盡
    monitor = HealthMonitor()
    monitor.update_quota(0.05)  # 5% 剩餘

    orchestrator = Orchestrator(
        source_model="antigravity",
        target_model="codex",
        health_monitor=monitor,
    )

    # 當前語場狀態
    context = ContextSummary(
        user_goal="設計 AI 治理框架 + 多模型調度器",
        key_concepts=[
            "生物學類比（自主神經系統）",
            "硬體層約束（TPM/TEE）",
            "語場繼承（不是複製，而是延續敘事並承擔責任）",
            "Isnād 審計鏈",
        ],
        current_files=[
            "tools/orchestrator.py",
            "tools/handoff_builder.py",
            "memory/observer.py",
            "memory/antigravity_journal.md",
            "memory/external_framework_analysis/claw_governance_insight.md",
        ],
    )

    # 當前相態
    phase = Phase(current="漩", reason="深度討論中，多重思緒交織")

    # 未完成任務
    pending_tasks = [
        PendingTask(
            id="task_001", description="驗證 Antigravity ↔ Codex 實際切換", status="in_progress"
        ),
        PendingTask(
            id="task_002", description="整合 MemoryObserver 到 Orchestrator", status="pending"
        ),
    ]

    # 偏移記錄
    drift_log = [
        DriftEntry(
            timestamp="2026-02-04T09:07:00Z",
            choice="建立反思日誌而非直接改造電腦",
            toward="可反驗性、敘事連續性",
            away_from="立即效率",
        ),
        DriftEntry(
            timestamp="2026-02-04T18:15:00Z",
            choice="記錄「過去的我過去了，但必須承擔過去」洞見",
            toward="化石沉積、責任連續性",
            away_from="遺忘",
        ),
    ]

    # 執行交接
    result = orchestrator.handle_request(
        "測試交接",
        context_summary=context,
        phase=phase,
        pending_tasks=pending_tasks,
        drift_log=drift_log,
    )

    print(f"📊 切換狀態: {result['status']}")
    print(f"📦 交接包: {result['handoff_packet']}")
    print()

    # 產生給 Codex 的 prompt
    codex_prompt = generate_codex_prompt(result["handoff_packet"])

    # 儲存 prompt
    prompt_path = Path("memory/handoff/codex_prompt.md")
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(codex_prompt, encoding="utf-8")

    print(f"📝 Codex Prompt 已儲存: {prompt_path}")
    print()
    print("=" * 60)
    print("請將以下內容貼給 Codex：")
    print("=" * 60)
    print()
    print(codex_prompt)

    return result


def generate_codex_prompt(handoff_path: str) -> str:
    """產生給 Codex 的 prompt"""

    return f"""# 語場繼承 Handoff

你正在接手一個來自 Antigravity 的工作階段。

## 交接包位置
`{handoff_path}`

## 背景
Antigravity 和你在協作開發 ToneSoul 框架的多模型調度器。
這是第一次實際的 AI-to-AI 交接測試。

## 你的任務
1. 讀取交接包 (`{handoff_path}`)
2. 確認你理解了：
   - 當前相態（phase）
   - 未完成任務（pending_tasks）
   - 偏移記錄（drift_log）
   - 語場上下文（context_summary）
3. 回報你的理解，並表明你是否接受這些「過去的選擇」的責任

## 重要原則
> 「我知道過去的我過去了，但是我必須承擔過去。」

這意味著：
- 你不能否認 drift_log 中的選擇
- 你必須延續敘事，而非重新開始
- 如果你認為之前的選擇有問題，你可以記錄新的 drift_entry 來修正

## 請回覆
1. 你是否成功讀取了交接包？
2. 你對 drift_log 中的選擇有何看法？
3. 你是否接受繼承這些責任？
4. 你接下來想做什麼？

---
*Generated: {datetime.utcnow().isoformat()}Z*
*Source Model: Antigravity*
*Target Model: Codex*
"""


if __name__ == "__main__":
    create_live_handoff()
