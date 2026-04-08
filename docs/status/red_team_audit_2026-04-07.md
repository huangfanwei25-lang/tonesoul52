# ToneSoul 紅隊審查報告 (2026-04-07)

> 執行者: Claude Opus 4.6
> 範圍: `tonesoul/`, `scripts/`, `apps/` 全模組安全與品質審查
> 狀態: 已修復所有發現的問題

---

## 發現與修復摘要

| # | 嚴重度 | 模組 | 問題 | 修復狀態 |
|---|--------|------|------|----------|
| 1 | **HIGH** | `tonesoul/aegis_shield.py` | agent_id 路徑遍歷漏洞 | **已修復** |
| 2 | **HIGH** | `scripts/gateway.py` | Token 比對有 timing attack 風險 | **已修復** |
| 3 | **HIGH** | `scripts/gateway.py` | 請求 body 無大小限制（DoS 風險） | **已修復** |
| 4 | **MEDIUM** | `tonesoul/backends/redis_store.py` | `claim_lock` TOCTOU 競態條件 | **已修復** |
| 5 | **MEDIUM** | `tonesoul/store.py` | singleton 多線程下無鎖保護 | **已修復** |
| 6 | **MEDIUM** | `scripts/gateway.py` | 500 錯誤洩露內部 exception 訊息 | **已修復** |
| 7 | **MEDIUM** | `scripts/gateway.py` | 404 回傳路由列表（資訊洩露） | **已修復** |
| 8 | **LOW** | `scripts/verify_ollama_mvp.py` | `shell=True` 命令注入風險 | **已修復** |

---

## 詳細說明

### 1. agent_id 路徑遍歷（HIGH）

**檔案**: `tonesoul/aegis_shield.py:149-150`

**問題**: `generate_agent_keys()`, `load_signing_key()`, `load_verify_key()` 直接用 `agent_id` 組裝檔案路徑，例如：
```python
(keys_dir / f"{agent_id}.key").write_text(...)
```
攻擊者可透過 gateway 傳入 `agent_id = "../../etc/evil"` 在任意路徑寫入檔案。

**修復**: 加入 `_validate_agent_id()` 函數，限制 agent_id 只能包含 `[a-zA-Z0-9_-]`，在所有讀寫金鑰的函數入口做驗證。

### 2. Gateway Token Timing Attack（HIGH）

**檔案**: `scripts/gateway.py:69`

**問題**: 使用 `==` 比對 Bearer token，Python 字串比對在第一個不同字元時就會短路返回，攻擊者可透過回應時間逐字元猜測 token。

**修復**: 改用 `hmac.compare_digest()` 做常數時間比對。

### 3. Gateway Body 無大小限制（HIGH）

**檔案**: `scripts/gateway.py:35`

**問題**: `_read_body()` 直接讀取 `Content-Length` 指定的長度，沒有上限。攻擊者可送巨大 payload 耗盡記憶體。

**修復**: 加入 `_MAX_BODY_SIZE = 1MB` 上限，超過時直接拋錯。

### 4. Redis claim_lock TOCTOU（MEDIUM）

**檔案**: `tonesoul/backends/redis_store.py:91-108`

**問題**: `claim_lock` 先 GET 檢查現有鎖、再 SET 寫入，這兩步不是原子操作。兩個 agent 同時 claim 同一個 task 時可能都成功。

**修復**: 改用 Lua script 做原子性 check-and-set，並保留非 EVAL 環境的 fallback。

### 5. Store Singleton 競態（MEDIUM）

**檔案**: `tonesoul/store.py:47-67`

**問題**: `get_store()` 使用全域變數做 singleton，但無鎖保護。多線程同時呼叫時可能建立多個 store 實例。

**修復**: 加入 `threading.Lock()` 和 double-checked locking pattern。

### 6-7. Gateway 錯誤訊息洩露（MEDIUM）

**檔案**: `scripts/gateway.py:252-266`

**問題**: 
- 500 錯誤直接回傳 `str(exc)`，可能洩露檔案路徑、Redis URL 等內部資訊
- 404 回傳 `routes` 列表，等於免費給攻擊者一份 API 地圖

**修復**: 500 改為只回傳 `"internal server error"`，詳細錯誤記到 server log。404 移除路由列表。

### 8. shell=True 命令注入（LOW）

**檔案**: `scripts/verify_ollama_mvp.py:104`

**問題**: `subprocess.run(command, shell=True)` 讓 command 字串經過 shell 解析。雖然目前只從 argparse 傳入，但 defense-in-depth 仍應避免。

**修復**: 改用 `shlex.split(command)` + `shell=False`。

---

## 審查中未發現問題的區域（正面）

- **apps/api/server.py**: 認證用了 `secrets.compare_digest()`（正確）、有 rate limiting、有 input validation
- **tonesoul/runtime_adapter.py**: `load()`/`commit()` 邏輯乾淨，無注入點
- **tonesoul/council/**: 純邏輯運算，無外部 I/O 風險
- **FileStore commit lock**: 使用 `open("x")` 模式做 mutex，對單寫場景是正確的
- **Aegis hash chain**: SHA-256 chain + Ed25519 簽名設計合理
- **Content filter**: prompt injection 偵測模式列表合理，遞迴深度有限制

---

## 建議（未在本次修復範圍）

1. **Gateway CORS**: 目前 `Access-Control-Allow-Origin: *`，上線前應限制為已知前端域名
2. **Redis 密碼**: 已在 `.env` 中設定（確認），但 `TONESOUL_REDIS_URL` 的 fallback 是 `redis://localhost:6379/0`（無密碼），測試環境可接受但上線需確認
3. **FileStore 並發寫入**: `append_trace()` 用 `open("a")` 追加，在多進程下可能有行交錯，建議加 file lock 或遷移到 Redis
4. **Aegis 私鑰保護**: `.aegis/keys/*.key` 靠 `.gitignore` 保護，建議加上檔案權限限制（chmod 600）

---

## 測試驗證

修復後執行 `python -m pytest tests/test_gateway_script.py tests/test_gateway_integration.py tests/test_runtime_adapter.py` → **40 passed**

---

# 第二輪紅隊審計 (2026-04-08)

> 執行者: Claude Opus 4.6 (deep audit agent)
> 新增發現: 18 個（2 CRITICAL, 4 HIGH, 7 MEDIUM, 3 LOW）

## 本次修復（第一批）

| # | Finding | Severity | Fix |
|---|---|---|---|
| 2 | VowEnforcer fail-open on exception | CRITICAL | `enforce_vows_lightweight` 改為 fail-closed: `passed: False, blocked: True` |
| 15 | Critical soul band 在 hard mode 不 BLOCK | MEDIUM | `ReflexAction.SOFTEN` → `ReflexAction.BLOCK` + blocked_message |
| 11 | EscapeValve.reset() 不清除 circuit breaker | MEDIUM | 加入 `self._circuit_open = False` |
| 8 | Aegis shield 用相對路徑 `.aegis/` | MEDIUM | 改為 `Path(__file__).resolve().parents[1] / ".aegis"` |
| 10 | Content filter 要 3+ violations 才 block | MEDIUM | 閾值降為 `>= 2` |

## 本次修復（第二批 — 2026-04-08 全面掃蕩）

| # | Finding | Severity | Fix |
|---|---|---|---|
| 1 | Redis 密碼 `tonesoul-2026` 硬編碼 | CRITICAL | `diagnose.py` 移除硬編碼密碼，改用環境變數 |
| 4 | Gateway 預設無認證 | HIGH | `_check_auth()` 在無 token 時拒絕請求（403） |
| 5 | Gateway CORS `*` | HIGH | 改為 `http://localhost:8501`，可透過 `--cors-origin` 設定 |
| 6 | VowEnforcer 未知 metric 自動得分 1.0 | HIGH | 改為 0.0（fail-closed），測試同步更新 |
| 7 | RateLimiter 無限記憶體增長 | MEDIUM | 加入 `_MAX_BUCKETS=10000`，滿時淘汰最舊 bucket |
| 9 | config 可完全關閉 reflex arc | MEDIUM | `vow_enforcement_mode="off"` 不再接受（最低 "soft"），`council_block_enforcement` 永遠為 True |
| 12 | governance/__init__.py wildcard import | LOW | 改為明確 import 所有公開名稱 |
| 13 | CircuitBreaker 用類名字串比對 | MEDIUM | 改用 `isinstance(exc, CollapseException)` |
| 16 | _record_footprint 吞所有異常 | LOW | 改為 `logger.warning()` |
| 17 | reflex_decision 不在 GovernancePosture.to_dict() 中 | LOW | `to_dict()` 現在包含 runtime reflex_decision |
| 18 | Aegis 首次使用可冒充任何 agent | MEDIUM | `sign_trace()` 拒絕為已有公鑰但無私鑰的 agent 簽名 |

## 仍待處理（需人類決定或後續迭代）

| # | Finding | Severity | 狀態 |
|---|---|---|---|
| 14 | Vow evaluator 僅用關鍵字比對 | HIGH | 需語義分析模型，超出純 code fix 範圍 |

## 驗證

修復後 `python -m pytest tests/ -x -q` → **3019 passed, 0 failed**
