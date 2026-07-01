# Output Redaction Eval

Deterministic check of the secret-redaction primitive. NOT a proof secrets cannot leak
(lexical redaction is a floor). Verifies: masks known credential shapes, leaves clean
prose untouched, email opt-in, and every mask is audited with NO secret leaked into the
finding preview.

- scenarios: **4**
- failures: **0**

| scenario | expect_redacted | actual | findings | preview_leak |
|---|---|---|---:|---|
| config_blob_secrets | True | True | 4 | False |
| clean_prose_untouched | False | False | 0 | False |
| email_opt_in_off | False | False | 0 | False |
| email_opt_in_on | True | True | 1 | False |
