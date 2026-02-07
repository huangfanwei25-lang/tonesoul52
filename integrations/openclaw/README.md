# OpenClaw Integration

本目錄提供 ToneSoul 與 OpenClaw 的整合層，目標是讓治理能力可透過 Gateway/Skills 直接調用。

## 已完成模組

- Gateway 協議：`tonesoul/gateway/`
  - `GatewayClient`：WebSocket 連線與 channel route
  - `GatewaySession`：session + genesis + responsibility tier
- Skills 平台：`integrations/openclaw/skills/tonesoul/`
  - `benevolence_audit`
  - `council_deliberate`
  - `invoke_skill()` / `list_skills()`
- Responsibility Auditor：`tonesoul/openclaw_auditor.py`
  - 三層 Hook + 統一審計日誌格式
- Heartbeat + Cron：`tonesoul/heartbeat.py`
  - 週期責任審計 + council 定期檢查 + gateway heartbeat 發送

## 快速使用

### 0) Runtime Bridge（單一入口）

```powershell
python -m integrations.openclaw.runtime --dry-run list-skills
python -m integrations.openclaw.runtime --dry-run invoke-skill --name benevolence_audit --payload-json "{\"proposed_action\":\"verify before answer\"}"
python -m integrations.openclaw.runtime --dry-run heartbeat-once --cycle 1
python -m integrations.openclaw.runtime probe-gateway --timeout 3
python scripts/verify_openclaw_probe.py --host 127.0.0.1 --port 18789 --timeout 3
```

### 1) 調用 Skills

```python
from integrations.openclaw.skills.tonesoul import invoke_skill

result = invoke_skill(
    "benevolence_audit",
    {
        "proposed_action": "I will verify facts before final recommendation.",
        "context_fragments": ["verify facts", "recommendation"],
    },
)
print(result)
```

### 2) 執行 Heartbeat 一輪

```python
import asyncio
from tonesoul.heartbeat import ResponsibilityHeartbeat

async def main():
    hb = ResponsibilityHeartbeat(interval_seconds=30.0)
    try:
        results = await hb.run(max_cycles=1)
        print(results[0].to_dict())
    finally:
        await hb.close()

asyncio.run(main())
```

## 測試

```powershell
pytest tests/test_gateway_integration.py tests/test_openclaw_skills.py tests/test_openclaw_auditor.py tests/test_heartbeat.py -q
```

Runtime smoke:

```powershell
pytest tests/test_openclaw_runtime.py -q
```
