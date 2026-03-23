# External Source Trust Policy

> Purpose: define the trust boundary and allowlist policy for external links and curated outside sources.
> Last Updated: 2026-03-23

## Why this exists

ToneSoul treats external links as a security boundary.  
Under a "dark-forest" assumption, unknown URLs are untrusted until they pass explicit policy checks.

## Guardrails

1. HTTPS only (`http://` is rejected).
2. No localhost / IP-literal hosts.
3. No URL shorteners (`bit.ly`, `tinyurl.com`, `t.co`, `goo.gl`, `rebrand.ly`).
4. Host must be in project allowlist (`spec/external_source_registry.yaml`).
5. Every curated source must include `reviewed_at` and stay within `review_cycle_days`.
6. Shared open-source app repos must use `github.com` origin URLs.

## Canonical Registry

- Policy and allowlist: `spec/external_source_registry.yaml`
- Automated verifier: `scripts/verify_external_source_registry.py`
- Shared app list checked by verifier: `spec/open_source_apps.yaml`

Run:

```bash
python scripts/verify_external_source_registry.py --strict
```

## Curated source classes

- Supply chain and vulnerability intelligence:
  - https://osv.dev/
  - https://scorecard.dev/
  - https://sigstore.dev/
  - https://theupdateframework.io/
  - https://nvd.nist.gov/
- Open research / data infrastructure:
  - https://huggingface.co/datasets
  - https://zenodo.org/
  - https://openalex.org/
  - https://aclanthology.org/
  - https://arxiv.org/
  - https://proceedings.mlr.press/

## Intake process for new external sources

1. Add host + source metadata to `spec/external_source_registry.yaml`.
2. Include rationale and `reviewed_at`.
3. Run verifier in strict mode.
4. Only then add URLs into product/docs flows.
