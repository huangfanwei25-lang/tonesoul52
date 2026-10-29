# Primary-source shadow replay

This is a curated retrospective case, not a blind benchmark or a forecast. The source is
TSMC's own 2026-02-10 release, retrieved directly over HTTPS on 2026-10-29. Two short,
non-contiguous snippets were checked against the response. See retrieval.json for the
retrieval receipt. The full HTML is not distributed; its hash alone does not authenticate it.

The second claim restates an unresolved historical-data conflict (2025 EPS around 120).
The original speaker video and EPS basis are not verified; it must not be called a failed
speaker prediction. The third claim is an explicitly constructed future hypothesis used as
an applicability control, not a real forecast. Semantic reviews were written by the assistant
with access to the source. The software checks consistency of these declarations; it does not
independently infer the financial contradiction.

Run from repository root:

```
python -m tonesoul.cli review examples/evidence_shadow/claims.txt --json
python -m tonesoul.cli review examples/evidence_shadow/claims.txt --json --evidence-case examples/evidence_shadow/case.json
```

Baseline wording review returns zero findings on this selected text. The sidecar preserves
those findings and adds: one narrowly supported historical statement, one insufficiently
supported historical record, and one future hypothesis not established by historical data.
All quotes match exactly; quotation match alone would not distinguish these claims.
The two blocked reviews are evidence insufficiency, NOT two proven false statements.

No precision/recall estimate is possible from this hand-selected example. Broad false-positive
and miss rates remain unmeasured. Reports carry no trading permission or forecast-scoring
eligibility. A source/claim/scope change invalidates prior review bindings. Review identities,
source labels and semantic assessments are declared, not authenticated.

The sidecar is optional. Without it, ts review behaves as before. Invalid sidecar input exits 3;
valid advisory findings retain exit 0. This CLI integration is not an always-on council hook.
