# ToneSoul 架構與依賴診斷報告

> Generated: 2026-03-31T00:25+08
> Agent: antigravity-opus
> Python: 3.13.5 (Windows)
> Commit: 6d6538e

---

## 1. 環境掃描結果

### Python 依賴

| 套件 | 狀態 | 用途 | 對應 pyproject.toml |
|------|------|------|---------------------|
| flask | ✅ 已安裝 | API gateway | core |
| numpy | ✅ 已安裝 | 張力計算 | core |
| pydantic | ✅ 已安裝 | Schema validation | core |
| rich | ✅ 已安裝 | CLI output | core |
| pytest / pytest-cov | ✅ 已安裝 | 測試 | dev |
| freezegun | ✅ 已安裝 | 時間凍結測試 | dev |
| hypothesis | ✅ 已安裝 | Property testing | dev |
| chromadb | ✅ 已安裝 | Vector DB (optional) | optional |
| ollama | ✅ 已安裝 | Local LLM | optional |
| sentence-transformers | ✅ 已安裝 | Embeddings | optional |
| streamlit | ✅ 已安裝 | Dashboard | optional[dashboard] |
| pandas | ✅ 已安裝 | Data | optional[dashboard] |
| **redis** | ❌ **未安裝** | Live coordination | **未列入 pyproject.toml** |
| **pynacl** | ❌ **未安裝** | Aegis Shield 簽名 | **未列入 pyproject.toml** |
| **psutil** | ❌ **未安裝** | System monitoring | **未列入 pyproject.toml** |
| plotly | ❌ 未安裝 | Dashboard charts | optional[dashboard] |

### 關鍵觀察

1. **redis**: `tonesoul/store.py` 在 `try/except` 裡 import，缺失時 graceful fallback 到 FileStore → ✅ 正確設計
2. **pynacl (nacl)**: `tonesoul/aegis_shield.py` 在 `try/except ImportError` 裡 import → ✅ graceful skip
3. **psutil**: 未在核心路徑使用，只在 optional monitoring scripts → ✅ 不影響核心
4. **plotly**: `pyproject.toml` 列在 `[dashboard]` optional group，但目前 `launch_dashboard.py` 實際上用的是純 HTML + JS → ✅ 不影響可運行性

> [!IMPORTANT]
> redis、pynacl、psutil 雖然 runtime 不會爆炸（設計了 fallback），但**應該寫入 pyproject.toml 的 optional dependencies**，否則新開發者無法知道這些功能存在。

---

## 2. 已觸碰的架構問題

### 問題 A: subprocess 嵌套在 Windows 上卡死

**嚴重度**: 🔴 高（阻塞整個 observer-window CLI）

**現象**: `run_observer_window.py` 呼叫 `subprocess.run([python, start_agent_session.py, ...])` → **永久 hang**（Windows 上 stdout buffering + `_quiet_call` redirect 衝突）

**受影響的腳本**:
| 腳本 | subprocess 目標 | 影響 |
|------|------------------|------|
| ~~`run_observer_window.py`~~ | ~~start_agent_session.py~~ | ✅ **已修復**（改為直接 import） |
| `run_launch_continuity_validation_wave.py` | start_agent_session.py | ⚠️ 可能卡死 |
| `run_collaborator_beta_preflight.py` | start_agent_session.py + run_r_memory_packet.py | ⚠️ 可能卡死 |

**根因**: `start_agent_session.py` 執行時 `_quiet_call(load, ...)` 會觸發 `store.py` 的 `get_store()` → 試圖連 Redis → 0.5s timeout。在 subprocess 模式下，`redirect_stdout` 後的 stdout handle 在 Windows 上可能和父程式的 `capture_output=True` 衝突，導致 pipe 死鎖。

**修復方案**: 將這兩個腳本也改為直接 import `_build_readiness` / `_build_import_posture`，而非 subprocess 嵌套。

---

### 問題 B: import_posture 結構不一致

**嚴重度**: 🟡 中

**現象**: `start_agent_session._build_import_posture()` 返回 `{"surfaces": {"posture": {...}, ...}, "summary_text": ...}`，但 `observer_window.py` 的 `_build_stable()` 讀 `import_posture["posture"]`（假設 surfaces 在頂層）。

**已修復**: `run_observer_window.py` 加了 unwrap: `import_posture = raw.get("surfaces") or raw`

**未來建議**: 如果更多消費者需要讀 import_posture，應該在 `start_agent_session.py` 裡把 `_build_import_posture` 的返回格式文件化，或提供一個 unwrap helper。

---

### 問題 C: pyproject.toml 缺少 optional dependency groups

**嚴重度**: 🟡 中

現有：
```toml
[project.optional-dependencies]
dashboard = ["streamlit>=1.28", "pandas>=2.0", "plotly>=5.0"]
dev = ["pytest>=7.0", ...]
ystm_viz = ["cairosvg>=2.7", "pillow>=10.0"]
```

缺少：
```toml
redis = ["redis>=4.5"]         # tonesoul/store.py, tonesoul/backends/redis_store.py
aegis = ["pynacl>=1.5"]        # tonesoul/aegis_shield.py (trace signing/verification)
monitoring = ["psutil>=5.9"]   # scripts/healthcheck.py
```

---

## 3. 腳本分類與可運行性

| 類型 | 腳本數量 | 可直接運行 | 需外部依賴 |
|------|----------|-----------|-----------|
| Session lifecycle | 5 | ✅ | - |
| Observer / diagnostic | 3 | ✅（修復後） | - |
| Verification (CI) | 17 | ✅ | git |
| Dashboard | 1 | ✅ | - |
| Market / trading | 6 | ⚠️ | finmind, API keys |
| LLM / chat | 4 | ⚠️ | ollama server |
| Memory consolidation | 6 | ✅ | - |
| Governance reports | ~30+ | ✅ | - |

---

## 4. 建議行動

### 立即（此次 session）
- [x] ~~修復 `run_observer_window.py` subprocess hang~~
- [x] ~~修復 import_posture unwrap~~
- [ ] 更新 pyproject.toml 補上 optional dependencies

### 短期（後續 session）
- [ ] 修復 `run_launch_continuity_validation_wave.py` 的 subprocess 嵌套
- [ ] 修復 `run_collaborator_beta_preflight.py` 的 subprocess 嵌套
- [ ] 在 `docs/GETTING_STARTED.md` 補充 Windows 特定注意事項

### 不做（by design）
- Redis 安裝：FileStore 是 launch default，Redis 是 optional runtime override
- PyNaCl 安裝：Aegis 簽名是 optional hardening，skip 時 graceful degrade
- psutil 安裝：只有 monitoring 用，不在核心路徑
