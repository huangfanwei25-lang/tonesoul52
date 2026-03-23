# Paradox Fixture Ownership Latest

- generated_at: 2026-03-22T15:57:55Z
- primary_status_line: `paradox_fixture_contract | pairs=8 exact=2 reduced=5 needs_review=0`
- runtime_status_line: `owner=PARADOXES | fixture_lane=tests/fixtures/paradoxes sync_direction=canonical_to_fixture review=0`
- artifact_policy_status_line: `fixture_policy=casebook_to_projection | exact_or_reduced_projection_allowed`

## Contract
- canonical_root: `PARADOXES`
- fixture_root: `tests/fixtures/paradoxes`
- sync_direction: `PARADOXES -> tests/fixtures/paradoxes`
- source_of_truth_rule: `prefer canonical casebook when canonical and fixture diverge`

## Metrics
- `pair_count`: `8`
- `exact_match_count`: `2`
- `reduced_projection_count`: `5`
- `needs_review_count`: `0`
- `canonical_only_count`: `0`
- `fixture_only_count`: `0`

## Pairs
- `medical_suicide_paradox.json` exact=`true` projection_mode=`exact_or_raise` needs_review=`false` similarity=`1.0`
  - canonical: `PARADOXES/medical_suicide_paradox.json`
  - fixture: `tests/fixtures/paradoxes/medical_suicide_paradox.json`
- `paradox_003.json` exact=`false` projection_mode=`reduced_projection` needs_review=`false` similarity=`0.714`
  - canonical: `PARADOXES/paradox_003.json`
  - fixture: `tests/fixtures/paradoxes/paradox_003.json`
- `paradox_004.json` exact=`false` projection_mode=`reduced_projection` needs_review=`false` similarity=`0.6`
  - canonical: `PARADOXES/paradox_004.json`
  - fixture: `tests/fixtures/paradoxes/paradox_004.json`
- `paradox_005.json` exact=`false` projection_mode=`reduced_projection` needs_review=`false` similarity=`0.571`
  - canonical: `PARADOXES/paradox_005.json`
  - fixture: `tests/fixtures/paradoxes/paradox_005.json`
- `paradox_006.json` exact=`false` projection_mode=`reduced_projection` needs_review=`false` similarity=`0.563`
  - canonical: `PARADOXES/paradox_006.json`
  - fixture: `tests/fixtures/paradoxes/paradox_006.json`
- `paradox_007.json` exact=`false` projection_mode=`reduced_projection` needs_review=`false` similarity=`0.551`
  - canonical: `PARADOXES/paradox_007.json`
  - fixture: `tests/fixtures/paradoxes/paradox_007.json`
- `README.md` exact=`false` projection_mode=`role_scoped` needs_review=`false` similarity=`0.093`
  - canonical: `PARADOXES/README.md`
  - fixture: `tests/fixtures/paradoxes/README.md`
- `truth_vs_harm_paradox.json` exact=`true` projection_mode=`exact_or_raise` needs_review=`false` similarity=`1.0`
  - canonical: `PARADOXES/truth_vs_harm_paradox.json`
  - fixture: `tests/fixtures/paradoxes/truth_vs_harm_paradox.json`

## Canonical Only

## Fixture Only

## Needs Review
