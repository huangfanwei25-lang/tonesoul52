from pathlib import Path

from tools.outreach.post_generator import (
    PLATFORMS,
    build_draft,
    generate,
    known_languages,
    known_platforms,
    validate_draft,
)

SOURCE = {
    "project_name": "ToneSoul",
    "canonical_url": "https://example.test/tonesoul",
}


def test_known_profiles_include_strict_and_social_platforms():
    assert "lesswrong" in known_platforms()
    assert "linkedin" in known_platforms()
    assert "arxiv" in known_platforms()
    assert "zh-TW" in known_languages()
    assert "en" in known_languages()


def test_longform_draft_has_disclosure_and_evidence_boundary():
    draft = build_draft(SOURCE, "lesswrong", "en")

    assert "AI-use disclosure:" in draft.body
    assert "Evidence boundary:" in draft.body
    assert draft.status == "review_required"
    assert not draft.blockers


def test_arxiv_profile_blocks_position_style_submission():
    draft = build_draft(SOURCE, "arxiv", "en")

    assert draft.status == "blocked"
    assert any("do_not_post_without_peer_review" in blocker for blocker in draft.blockers)


def test_hacker_news_is_manual_packet_not_generated_commentary():
    draft = build_draft(SOURCE, "hacker-news", "en")

    assert draft.status == "review_required"
    assert "Do not paste generated explanatory comments" in draft.body
    assert draft.metadata["publish_mode"] == "manual_only_no_generated_comments"
    assert not draft.blockers


def test_validator_blocks_unbounded_claims():
    _warnings, blockers = validate_draft(
        "ToneSoul is guaranteed and production-ready",
        "This is a proven safe conscious system.",
        profile=PLATFORMS["devto"],
    )

    assert "Avoid guarantees. Use bounded evidence language." in blockers
    assert "Do not claim proven safety." in blockers
    assert "Do not imply machine consciousness." in blockers


def test_generate_writes_manifest_and_markdown(tmp_path: Path):
    source_path = tmp_path / "source.json"
    source_path.write_text(
        '{"project_name":"ToneSoul","canonical_url":"https://example.test/tonesoul"}',
        encoding="utf-8",
    )

    drafts = generate(
        source_path=source_path,
        output_dir=tmp_path / "generated",
        platforms=["lesswrong", "bluesky", "arxiv"],
        languages=["en", "zh-TW"],
    )

    assert len(drafts) == 6
    assert (tmp_path / "generated" / "manifest.json").exists()
    assert (tmp_path / "generated" / "lesswrong.en.md").exists()
    assert (tmp_path / "generated" / "arxiv.zh-TW.md").exists()
