from tonesoul52.tech_trace.normalize import normalize_record


def test_normalize_record_auto_claims() -> None:
    payload = normalize_record(
        raw_text="First claim. Second claim!",
        capture_id=None,
        source={},
        source_grade=None,
        summary=None,
        notes=None,
        tags=None,
        max_length=None,
        claims=None,
        links=None,
        attributions=None,
        auto_claims=True,
        auto_claim_limit=2,
        auto_claim_min_chars=5,
    )
    claims = payload.get("claims")
    assert isinstance(claims, list)
    assert len(claims) == 2
