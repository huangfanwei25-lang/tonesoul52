"""
Orchestrator Integration Test - 測試切換機制

展示：
1. 正常運行（不切換）
2. 模擬 quota 用盡觸發 handoff
3. MemoryObserver 自動記錄
"""

import sys
sys.path.insert(0, ".")

from tools.orchestrator import (
    Orchestrator,
    HealthMonitor,
    DecisionEngine,
    InstanceLauncher,
)
from tools.handoff_builder import (
    Phase,
    PendingTask,
    DriftEntry,
    ContextSummary,
)
from memory.observer import MemoryObserver


def test_normal_operation():
    """測試正常運行（不觸發切換）"""
    print("=" * 50)
    print("Test 1: 正常運行（不切換）")
    print("=" * 50)
    
    orchestrator = Orchestrator(
        source_model="antigravity",
        target_model="codex",
    )
    
    context = ContextSummary(
        user_goal="測試調度器",
        key_concepts=["handoff", "health monitor"],
        current_files=["tests/test_orchestrator.py"],
    )
    
    result = orchestrator.handle_request(
        "這是一個正常的請求",
        context_summary=context,
    )
    
    print(f"Status: {result['status']}")
    print(f"Switched: {result['switched']}")
    print(f"Health: quota={result['health'].quota_remaining}, failures={result['health'].consecutive_failures}")
    print()
    
    return result["switched"] == False


def test_quota_exhausted():
    """測試 quota 用盡觸發切換"""
    print("=" * 50)
    print("Test 2: Quota 用盡（觸發 handoff）")
    print("=" * 50)
    
    # 建立一個 quota 即將用盡的 monitor
    health_monitor = HealthMonitor()
    health_monitor.update_quota(0.05)  # 只剩 5%
    
    orchestrator = Orchestrator(
        source_model="antigravity",
        target_model="codex",
        health_monitor=health_monitor,
    )
    
    context = ContextSummary(
        user_goal="測試 quota 用盡切換",
        key_concepts=["handoff", "quota", "switch"],
        current_files=["tests/test_orchestrator.py"],
    )
    
    result = orchestrator.handle_request(
        "Quota 即將用盡的請求",
        context_summary=context,
        phase=Phase(current="霧", reason="多重未定"),
        pending_tasks=[
            PendingTask(id="task_001", description="完成調度器測試", status="in_progress")
        ],
        drift_log=[
            DriftEntry(
                timestamp="2026-02-04T18:00:00Z",
                choice="選擇自我審計而非外部審計",
                toward="自主性",
                away_from="效率",
            )
        ],
    )
    
    print(f"Status: {result['status']}")
    print(f"Switched: {result['switched']}")
    print(f"Handoff Packet: {result.get('handoff_packet', 'N/A')}")
    print(f"Launch Info: {result.get('launch', 'N/A')}")
    print()
    
    return result["switched"] == True


def test_with_observer():
    """測試與 MemoryObserver 整合"""
    print("=" * 50)
    print("Test 3: MemoryObserver 整合")
    print("=" * 50)
    
    observer = MemoryObserver()
    
    # 記錄一個 action
    action_id = observer.log_action(
        action="handle_request",
        params={"input": "測試請求"},
        result={"status": "ok"},
        before_context={"phase": "霧"},
        after_context={"phase": "雪"},
    )
    print(f"Action logged: {action_id}")
    
    # 記錄一個 commitment
    commitment_id = observer.log_commitment(
        vow="語場繼承的目標是延續敘事並承擔責任",
        falsifiable_by="交接後的 AI 否認 drift_log 中的選擇",
        measurable_via="drift_log 連續性檢查",
    )
    print(f"Commitment logged: {commitment_id}")
    
    # 查詢最近的記錄
    logs = observer.query(limit=5)
    print(f"Recent logs: {len(logs)} entries")
    for log in logs:
        print(f"  - {log.get('record_type')}: {log.get('action')}")
    print()
    
    return True


def main():
    print("\n🎛️ Orchestrator Integration Test")
    print("=" * 50)
    print()
    
    results = []
    
    results.append(("Normal Operation", test_normal_operation()))
    results.append(("Quota Exhausted", test_quota_exhausted()))
    results.append(("MemoryObserver", test_with_observer()))
    
    print("=" * 50)
    print("📊 Test Results")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
