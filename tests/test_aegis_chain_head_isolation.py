"""Regression: tests must not move the repo-global Aegis chain head.

Root cause finding (docs/plans/aegis_chain_head_test_pollution_2026-07-05.md):
AegisShield.save()'s file lane writes the module-level _AEGIS_DIR, so any
test reaching a real commit() advanced the repo's .aegis/chain_head.txt
while its trace log stayed isolated — the recurring benign 'compromised'
gap. The conftest autouse fixture now redirects _AEGIS_DIR per-test; these
tests pin that isolation at the exact seam (save/load), independently
adjudicated 2026-07-05 (honest-judgment D3: monkeypatch shape preferred
over env override — production surface unchanged).
"""

import tonesoul.aegis_shield as aegis_shield


def _repo_head_bytes():
    real = aegis_shield._REPO_ROOT / ".aegis" / "chain_head.txt"
    return real.read_bytes() if real.exists() else None


def test_shield_save_cannot_touch_repo_chain_head():
    before = _repo_head_bytes()

    shield = aegis_shield.AegisShield(chain_head="isolation-regression-sentinel")
    shield.save()

    assert _repo_head_bytes() == before  # repo-global head untouched
    # The write landed in the per-test isolated dir instead.
    isolated = aegis_shield._AEGIS_DIR / "chain_head.txt"
    assert isolated.read_text(encoding="utf-8") == "isolation-regression-sentinel"
    assert aegis_shield._AEGIS_DIR != aegis_shield._REPO_ROOT / ".aegis"


def test_shield_load_reads_isolated_dir_not_repo():
    # Fresh isolated dir -> empty head, regardless of the repo's live head.
    # (In a clean clone both are empty; locally this catches a removed fixture
    # whenever the repo has a live chain head.)
    shield = aegis_shield.AegisShield.load()
    assert shield.chain_head == ""
