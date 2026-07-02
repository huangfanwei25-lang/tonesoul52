# codex 審查工單 — 本週同模型濃度最高的三塊(2026-07-03 排單)

> 排單原因:反證鏈(#247)、vow 撤回(#248/#249)、honest-judgment(#252/#254)
> 全部由 fable 寫、fable 驗——同模型盲點濃度是本週最高。codex 有算力時照單執行,
> 規則照 .claude/skills/codex-second-opinion(獨立判斷、describe-only、cross-check 歸人)。

## 工單 1:vow 撤回實作(優先,動了治理層)
`python scripts/codex_review.py --target tonesoul/vow_system.py "Review the WithdrawalTerms dataclass and VowRegistry.withdraw/withdrawal_records added 2026-07-02: (1) any path where withdraw() can affect enforcement beyond active=False; (2) mutation/aliasing of terms_snapshot; (3) serialization round-trip holes in to_dict/from_dict; (4) whether the exit ledger can be silently lost (registry lifetime/persistence)."`

## 工單 2:反證鏈 schema 擴充
`python scripts/codex_review.py --target tonesoul/accountability_panel.py "Review the method/outcome/evidence_ref extension: validation completeness, HTML injection via the new ceref suffix, legacy-record compatibility, and whether any consumer silently gates on these shadow fields."`

## 工單 3:honest-judgment 協議(design review)
`python scripts/codex_review.py --target .claude/skills/honest-judgment/SKILL.md "Adversarial design review: where does this protocol produce confident-sounding but weakly-grounded verdicts? Is the burden-of-proof default (on change) justified? Does the DECLARE_STANCE boundary leak (cases that should hand back but won't)? Is the degraded sequential mode honest enough?"`

完成後:AGREED/DISAGREED 分類歸人審,findings 進反證鏈(challenger=codex)。
