from __future__ import annotations

from tonesoul.output_redaction import has_secrets, redact


def test_masks_common_secret_shapes() -> None:
    cases = {
        "anthropic_openai_key": "key is sk-ant-api03-AbCdEf0123456789xyz done",
        "github_token": "token ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 end",
        "aws_access_key_id": "aws AKIAIOSFODNN7EXAMPLE here",
        "google_api_key": "g AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe x",
        "slack_token": "s xoxb-123456789012-abcdefghijkl end",
        "bearer": "Authorization: Bearer abcdefghijklmnopqrstuvwxyz0123456789",
    }
    for kind, text in cases.items():
        result = redact(text)
        assert result.redacted, kind
        assert f"[REDACTED:{kind}]" in result.text, kind
        assert result.findings[0].kind == kind


def test_private_key_block_masked_whole() -> None:
    text = "before\n-----BEGIN RSA PRIVATE KEY-----\nMIIabc\nxyz==\n-----END RSA PRIVATE KEY-----\nafter"
    result = redact(text)
    assert "[REDACTED:private_key]" in result.text
    assert "MIIabc" not in result.text
    assert result.text.startswith("before") and result.text.endswith("after")


def test_assignment_keeps_key_masks_value() -> None:
    result = redact('api_key="s3cr3tValue123" and password: hunter2xyz')
    assert "api_key=" in result.text and "password:" not in result.text.replace(
        "password: [REDACTED:assignment]", ""
    )  # key names preserved
    assert "s3cr3tValue123" not in result.text
    assert "hunter2xyz" not in result.text
    assert all(f.kind == "assignment" for f in result.findings)


def test_pii_email_is_opt_in() -> None:
    text = "contact me at person@example.com please"
    assert not redact(text).redacted  # secrets-only default: email NOT masked
    with_pii = redact(text, include_pii=True)
    assert with_pii.redacted and "[REDACTED:email]" in with_pii.text
    assert "person@example.com" not in with_pii.text


def test_clean_text_unchanged_and_no_findings() -> None:
    text = "Password protection is important; discuss the token economy of the council."
    result = redact(text)
    assert not result.redacted
    assert result.text == text  # no false positive on the bare words password/token/secret


def test_preview_never_leaks_the_secret() -> None:
    secret = "sk-ant-api03-DEADBEEF0123456789cafe"
    result = redact(f"k={secret}")
    assert result.findings
    for f in result.findings:
        # preview is kind + length only — must not contain the secret's characters
        assert secret not in f.preview
        assert "DEADBEEF" not in f.preview
        assert f.preview.endswith("chars)")


def test_overlap_not_double_counted() -> None:
    # an sk- key sitting in an assignment value: one masked span, not two overlapping ones
    result = redact("api_key=sk-ant-api03-AbCdEf0123456789xyz")
    assert len(result.findings) == 1
    spans = [(f.start, f.end) for f in result.findings]
    s0, e0 = spans[0]
    assert not any(s0 < e and e0 > s for (s, e) in spans[1:])  # trivially true; documents intent


def test_idempotent_on_already_redacted() -> None:
    once = redact("token=abcdef123456").text
    twice = redact(once)
    assert not twice.redacted  # the [REDACTED:...] marker matches no pattern
    assert twice.text == once


def test_findings_spans_are_on_original_text() -> None:
    text = "prefix sk-ant-api03-AbCdEf0123456789xyz suffix"
    result = redact(text)
    f = result.findings[0]
    assert text[f.start : f.end].startswith("sk-ant-")


def test_empty_input() -> None:
    r = redact("")
    assert r.text == "" and not r.redacted
    assert not has_secrets("")
