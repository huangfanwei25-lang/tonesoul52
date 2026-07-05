# 發現:Aegis chain head 被測試污染 — 「良性缺口復發」的根因(2026-07-05)

> Status: **FINDING + 提案工單;修不修、怎麼修 = owner 決定**(碰 Aegis = 治理層,owner-gated)。
> 發現者:claude-fable-5,2026-07-05 下午(PR #300 全套驗證後的 diagnose)。

## 症狀(可重現)

`diagnose` 反覆回報 `Aegis integrity: compromised`(0 簽章失敗、chain valid、僅 head/tail
anchor mismatch),`aegis_reanchor.py` 修好後**下一次跑完整測試套件又會復發**。時間軸證據
(2026-07-05):早上 re-anchor 至 intact(head `19d1da5d`)→ 下午全套 pytest(15:11-15:26)
→ `.aegis/chain_head.txt` mtime **15:26**、head 變 `4104ddae`、log tail 仍 `19d1da5d`、
total_traces 不變。歷史上 2026-07-03 也修過一次至 intact,同樣復發。

## 根因(機制,已讀碼)

`AegisShield.save()`(`tonesoul/aegis_shield.py:387-393`)的 file lane 寫死模組常數
`_AEGIS_DIR / "chain_head.txt"` ——**全域路徑,無 env/參數覆寫**。測試(如
`tests/test_runtime_adapter.py` 家族)跑真 `commit()` 時,session trace log 走測試自己的
temp 路徑,但 chain head 落到**倉庫的全域檔**:頭被推前、log 沒有對應 trace →
head/tail mismatch。這是 `feedback_runtime_state_pollutes_tests_and_vc`(2026-06-16)
判例家族的新成員:**測試隔離了資料面、沒隔離錨面**。

## 為什麼這重要(不只是煩)

- 每次復發都讓 `compromised` 這個字出現在 diagnose——**狼來了效應**:哪天真的被篡改,
  讀者已經習慣把 compromised 當雜訊。誠實系統不能讓自己的警報詞貶值。
- re-anchor 是對症不對因;修一次 ≠ 免疫(同 stale-reference 判例的形狀)。

## 提案工單(bounded;owner 點頭才派)

1. `_AEGIS_DIR` 改為可覆寫(env `TONESOUL_AEGIS_DIR`,預設不變)——單點改,fail-closed
   語義不動。
2. 測試側:conftest 或觸碰 commit() 的測試 fixture 設該 env 到 tmp。
3. 驗收:全套 pytest 前後 `.aegis/chain_head.txt` **hash 不變** + `diagnose` 保持 intact;
   加一個 regression test 直接斷言這件事。
4. 收尾跑一次 `aegis_reanchor.py --apply` 清掉最後一次污染。

## 暫行處置(本 session 已做)

再跑一次 re-anchor(同早上 owner 已核准的良性修復,dry-run 確認同形狀後 apply)。
在根因修掉之前,**每次全套測試後 head 都會再被推走**——診斷時看到 compromised,先對
本檔,別直接當入侵。
