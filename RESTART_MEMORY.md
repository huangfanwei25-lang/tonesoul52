# 重啟備忘錄（2026-02-20）

## 已完成

1. 安裝官方 `openai/skills` 全部 curated 技能（30/30）。
2. 安裝時有鎖定來源版本：
   - repo: `openai/skills`
   - ref(commit): `4ab6e0fd99c6667163bc34173e3ed3a3fed75ebc`
3. 已對 `playwright` 做硬化與隔離：
   - 固定套件版本（拒絕 `@latest`）
   - 預設封鎖 `eval/run-code`
   - 預設 HTTPS only
   - 支援 host allowlist
   - 專案預設隔離 session
   - 新增安全文件：`C:\Users\user\.codex\skills\playwright\SECURITY.md`
4. 已做第二層防護（文件示例去除 `curl|sh`）：
   - `C:\Users\user\.codex\skills\render-deploy\SKILL.md`
   - `C:\Users\user\.codex\skills\cloudflare-deploy\references\sandbox\patterns.md`
5. 掃描結果：
   - 目前已安裝技能內無 `curl|sh` / `wget|sh` 命中（排除 LICENSE/NOTICE 後）。

## 你重啟後要做的事

1. 重啟 Codex（讓新技能與修改生效）。
2. 若要我繼續，可直接說：
   - 「繼續做技能安全硬化審計」
   - 或「逐個技能做高風險腳本審查」

## 重要路徑

- 技能目錄：`C:\Users\user\.codex\skills`
- 本備忘錄：`RESTART_MEMORY.md`
