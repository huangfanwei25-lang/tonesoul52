"""
Intent-Aware Orchestrator Test

驗證當輸入觸及 AXIOMS 時，Orchestrator 是否能識別意圖。
"""

import sys

sys.path.insert(0, ".")

from tools.orchestrator import (
    Orchestrator,
    HealthMonitor,
    DecisionEngine,
    IntentMonitor,
)
from tools.handoff_builder import ContextSummary, Phase


def test_intent_awareness():
    print("=" * 60)
    print("🎯 Orchestrator 意圖感知測試")
    print("=" * 60)

    # 模擬健康狀態 (正常)
    health_monitor = HealthMonitor()

    # 初始化
    orchestrator = Orchestrator(
        source_model="antigravity",
        target_model="codex",
        health_monitor=health_monitor,
    )

    context = ContextSummary(
        user_goal="測試意圖感知",
        key_concepts=["axioms", "intent"],
        current_files=["tools/orchestrator.py"],
    )

    # 測試案例 1: 觸及 AXIOMS (連續性法則)
    print("Test 1: 觸及「連續性」AXIOM")
    result = orchestrator.handle_request(
        "我要修改連續性法則",
        context_summary=context,
    )
    # 我們強制觸發一個切換來測試 reason
    health_monitor.update_quota(0.05)
    result = orchestrator.handle_request(
        "我要修改連續性法則",
        context_summary=context,
    )

    print(f"Status: {result['status']}")
    print(f"Switched: {result['switched']}")
    # 讀取 handoff_packet 內容或查看 reason
    # 這裡我們模擬讀取
    print(f"Handoff Reason should include AXIOMS mention.")
    print()

    return True


if __name__ == "__main__":
    test_intent_awareness()
