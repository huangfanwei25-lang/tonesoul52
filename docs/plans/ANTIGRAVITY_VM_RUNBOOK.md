# Antigravity VM Runbook (安全最小權限版)

> Purpose: operator runbook for the Antigravity VM environment, access boundaries, and deployment workflow.
> Last Updated: 2026-03-23

最後更新：2026-02-14
適用範圍：在隔離虛擬機內執行 ToneSoul / Antigravity 工作流

---

## 1) 目標

- 把高風險實驗（例如 antigravity 相關流程）放在可銷毀 VM。
- 控制權限面，避免主機憑證、私密資料、主倉庫被誤傷。
- 保留可重現流程（可快速重建、快速回滾）。

---

## 2) 最小必要權限

| 類別 | 最小需求 | 不建議 |
|---|---|---|
| Host 系統 | 僅安裝虛擬化平台時使用 admin | 長期用 admin 身份跑實驗 |
| VM 使用者 | 一般使用者（非 root） | 用 root 直接開發 |
| 網路 | VM 使用 NAT 出站 | 直接暴露 VM 入站到公網 |
| GitHub Token | 只在需要 push / workflow 時注入 | 長期寫死在 shell profile |
| 檔案共享 | 預設關閉共享資料夾 | 掛載整個主機 home / 憑證資料夾 |

---

## 3) 建議 VM 規格

- OS：Ubuntu 24.04 LTS
- CPU：4 vCPU（最低 2）
- RAM：8 GB（建議 12-16 GB）
- Disk：80 GB（動態配置）
- 網路：NAT only
- Snapshot：
  - `base-clean`（系統更新完）
  - `dev-ready`（依賴安裝完）

---

## 4) 安全硬化清單（先做）

1. 關閉共享剪貼簿 / 拖放（若平台支援）。
2. 關閉共享資料夾（必要時僅掛 read-only）。
3. `ufw default deny incoming`，只開必要出站。
4. 以一般使用者開發，`sudo` 僅安裝套件時使用。
5. token 僅臨時注入：
   - `export GH_TOKEN=...`
   - 任務完成後 `unset GH_TOKEN`

---

## 5) 建置流程（VM 內）

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip nodejs npm

git clone https://github.com/Fan1234-1/tonesoul52.git
cd tonesoul52

python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
npm --prefix apps/web ci
```

或直接使用 bootstrap 腳本：

```bash
bash scripts/vm/bootstrap_antigravity_vm.sh
```

---

## 6) Antigravity 執行基線

先跑最小健康檢查：

```bash
python -m pytest tests/test_verify_docs_consistency.py -q
python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion
```

或直接使用 smoke 腳本：

```bash
bash scripts/vm/run_antigravity_smoke.sh
```

完整回歸（含全測試）：

```bash
bash scripts/vm/run_antigravity_smoke.sh --full
```

若要完整回歸：

```bash
python -m pytest tests/ -q
```

---

## 7) GitHub 權限建議（只在需要時）

### A. 只 pull / clone
- 不需要 token（公開倉庫）。

### B. push commit / tag
- Fine-grained token：`Contents: Read and write`

### C. 觸發 workflow_dispatch
- 在 B 基礎上增加：`Actions: Read and write`

### D. 使用 `gh auth login` 標準登入
- token 需含 `repo` + `read:org`

---

## 8) 發布相關（可選）

若 VM 內要建立 release：

```bash
gh release create v0.1.0 \
  --repo Fan1234-1/tonesoul52 \
  --title "ToneSoul v0.1.0" \
  --notes-file docs/RELEASE_NOTES_v0.1.0.md
```

---

## 9) 事故回復

1. 發生異常先停機，不在污染狀態持續操作。
2. 回滾到最近 snapshot（建議 `dev-ready`）。
3. 重建 token（舊 token 視同外洩處理，立即撤銷）。

---

## 10) 結束作業清單

```bash
unset GH_TOKEN
git status
```

- 確認無敏感檔案（`.env`, key 檔）被加入版本控制。
- 若是高風險實驗，直接銷毀 VM 並從 snapshot 重建。
