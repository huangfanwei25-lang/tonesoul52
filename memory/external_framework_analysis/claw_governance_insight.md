# AI 治理三層架構洞見

## 來源
外部觀察（Claw 生態系討論）

## 三層治理架構

### 1. CONSTITUTION (憲法層)
- **概念**: 不可修改的根本規則，如同 BIOS 或 OS runtime
- **儲存**: 外部不可變儲存 (Parameter Store, 環境變數)
- **特性**: 即使是用戶或 SKILL 也無法違反

### 2. Human Authorization (授權層)
- **概念**: 所有動作執行前需 human 授權
- **實現**: Telegram LGTM, TouchID, ORG Admin 審批
- **沙盒**: 未授權僅能在沙盒內運行
- **合規**: PII/PHI 去識別，符合 GDPR/HIPAA

### 3. Fully Auditable (審計層)
- **概念**: 所有動作 CloudTrail 可查
- **實現**: 完整執行記錄，可追溯

---

## ToneSoul 現狀對照

| 層 | 外部概念 | ToneSoul | 差距 |
|---|---------|----------|------|
| 憲法 | 不可變 Parameter Store | `law/AXIOMS.json` | ⚠️ 可被修改 |
| 授權 | Human-in-the-loop | Council 內部審議 | ⚠️ 無強制 HITL |
| 審計 | CloudTrail | Isnād + Hash Chain | ✅ 已實作 |

---

## 改進方向

### Phase 9: Immutable Constitution
- AXIOMS 存入環境變數或外部 KMS
- 啟動時 hash 驗證，不符則拒絕運行

### Phase 10: Human Authorization Gateway
- 高風險動作 → Telegram/Discord 通知 → 等待 LGTM
- 沙盒內動作 → 自動放行
- PII 偵測 → 自動去識別

---

## BSD 類比

| BSD 分支 | 設計哲學 | 類比 |
|---------|----------|------|
| FreeBSD | 易用性 + 穩定性 | 商業落地優先 |
| OpenBSD | 安全性優先 | ToneSoul 目前位置 |
| NetBSD | 可移植性 | 跨平台 Agent 框架 |

**目標**: 從 OpenBSD 思路往 FreeBSD 易用性發展，同時保持安全性。

*Recorded: 2026-02-04 | Source: Claw 生態系討論*
