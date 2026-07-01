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
    result = redact('api_key="s3cr3tValue123" and password=hunter2xyz')
    assert "api_key=" in result.text and "password=" in result.text  # key names preserved
    assert "s3cr3tValue123" not in result.text
    assert "hunter2xyz" not in result.text
    assert all(f.kind.startswith("assignment") for f in result.findings)


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


# --- regression tests for the codex (different-model) review, 2026-07-01 ---


def test_env_style_prefixed_keys_are_masked() -> None:
    # codex F1: the most common leak vector — env var names with a prefix.
    for line, secret in [
        ("OPENAI_API_KEY=abcdef1234567890", "abcdef1234567890"),
        ("DB_PASSWORD=hunter2supersecret", "hunter2supersecret"),
        ("AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY", "wJalrXUtnFEMI"),
        ("OAUTH_CLIENT_SECRET=abcdef1234567890", "abcdef1234567890"),
    ]:
        result = redact(line)
        assert result.redacted, line
        assert secret not in result.text, line


def test_connection_string_and_url_userinfo_masked() -> None:
    # codex F3: password embedded in a URI/connection string.
    for text, secret in [
        ("DATABASE_URL=postgres://alice:s3cr3tPassword@db.internal/app", "s3cr3tPassword"),
        ("visit https://alice:s3cr3tPassword@example.com/path now", "s3cr3tPassword"),
    ]:
        result = redact(text)
        assert result.redacted and secret not in result.text, text


def test_basic_auth_and_stripe_masked() -> None:
    # codex F3
    r1 = redact("Authorization: Basic dXNlcjpwYXNzd29yZDEyMw==")
    assert r1.redacted and "[REDACTED:basic_auth]" in r1.text and "dXNlcj" not in r1.text
    # assembled from parts so the secret shape never sits contiguously in git (push-protection),
    # while redact() still sees the full shape at runtime.
    stripe = "sk_" + "live_" + "51N9aBcDeFgHiJkLmNoPqRsTuVwXyZ01"
    r2 = redact(f"the key {stripe} leaked")
    assert r2.redacted and stripe not in r2.text


def test_sk_learn_is_not_a_false_positive() -> None:
    # codex F4: hyphenated prose starting sk- must NOT be redacted.
    text = "This package is sk-learn-compatible-model for demos."
    result = redact(text)
    assert not result.redacted
    assert result.text == text


def test_colon_prose_is_not_partially_eaten() -> None:
    # codex F5: an UNQUOTED value after ":" is prose-ambiguous, so not masked by default.
    text = "password: strong policy is required for all users."
    result = redact(text)
    assert not result.redacted
    assert result.text == text


def test_quoted_value_with_spaces_fully_masked() -> None:
    # codex F2: a quoted multi-word secret must be masked WHOLE — no tail left behind.
    result = redact('password = "correct horse battery staple"')
    assert result.redacted
    assert "correct" not in result.text and "staple" not in result.text
    assert "[REDACTED:assignment_quoted]" in result.text


# --- round-2 codex re-review regression tests, 2026-07-01 ---


def test_quoted_redaction_is_idempotent() -> None:
    # round-2 #1: assignment_quoted must not re-report a finding on its own marker.
    once = redact('password="correct horse battery staple"').text
    twice = redact(once)
    assert not twice.redacted and twice.text == once


def test_uri_password_with_colon_masked_whole() -> None:
    # round-2 #2: a password containing ":" must not leak its tail.
    r = redact("DATABASE_URL=postgres://alice:s3c:r3tPassword@db.internal/app")
    assert r.redacted
    assert "r3tPassword" not in r.text and "s3c:r3t" not in r.text


def test_secret_key_base_env_name_masked() -> None:
    # round-2 #3: the common Rails SECRET_KEY_BASE.
    r = redact("SECRET_KEY_BASE=abcdef1234567890abcdef")
    assert r.redacted and "abcdef1234567890abcdef" not in r.text


def test_inline_quoted_colon_prose_not_eaten() -> None:
    # round-2 #4: ":" mid-line is prose, not config — must NOT be redacted.
    text = 'note: password: "strong policy" is required for all'
    r = redact(text)
    assert not r.redacted and r.text == text


def test_yaml_line_start_colon_quoted_is_masked() -> None:
    # round-2 #4 (coverage half): a real line-start YAML secret IS masked.
    r = redact('  api_key: "s3cr3tValueHere"')
    assert r.redacted and "s3cr3tValueHere" not in r.text


def test_basic_auth_requires_authorization_header() -> None:
    # round-2 #5: bare "Basic <word>" in prose must not be redacted.
    prose = "The Basic abcdefghijklmnop section is not a credential."
    assert not redact(prose).redacted
    hdr = redact("Authorization: Basic " + "dXNlcjpwYXNzd29yZDEyMw==")
    assert hdr.redacted and "[REDACTED:basic_auth]" in hdr.text and "dXNlcj" not in hdr.text
