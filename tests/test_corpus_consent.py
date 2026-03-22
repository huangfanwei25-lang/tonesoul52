from tonesoul.corpus.consent import ConsentManager, ConsentType, create_consent_manager


def test_hash_identifier_handles_empty_and_is_stable():
    assert ConsentManager.hash_identifier("") == ""
    assert ConsentManager.hash_identifier("127.0.0.1") == ConsentManager.hash_identifier(
        "127.0.0.1"
    )
    assert len(ConsentManager.hash_identifier("127.0.0.1")) == 32


def test_record_and_get_consent_roundtrip_with_hashed_identifiers(tmp_path):
    manager = ConsentManager(str(tmp_path / "users.db"))

    recorded = manager.record_consent(
        "session-1",
        ConsentType.RESEARCH,
        ip_address="127.0.0.1",
        user_agent="pytest-agent",
    )
    loaded = manager.get_consent("session-1")

    assert recorded.ip_hash == ConsentManager.hash_identifier("127.0.0.1")
    assert recorded.user_agent_hash == ConsentManager.hash_identifier("pytest-agent")
    assert loaded is not None
    assert loaded.session_id == "session-1"
    assert loaded.consent_type is ConsentType.RESEARCH
    assert loaded.withdrawn is False
    assert loaded.to_dict()["consent_type"] == "research"


def test_has_valid_consent_tracks_absent_and_withdrawn_sessions(tmp_path):
    manager = ConsentManager(str(tmp_path / "users.db"))

    assert manager.has_valid_consent("missing") is False

    manager.record_consent("session-1", ConsentType.IMPROVEMENT)
    assert manager.has_valid_consent("session-1") is True

    manager.withdraw_consent("session-1")
    assert manager.has_valid_consent("session-1") is False


def test_withdraw_consent_returns_false_for_missing_session(tmp_path):
    manager = ConsentManager(str(tmp_path / "users.db"))

    assert manager.withdraw_consent("missing") is False


def test_get_consent_stats_counts_active_withdrawn_and_types(tmp_path):
    manager = ConsentManager(str(tmp_path / "users.db"))
    manager.record_consent("session-1", ConsentType.RESEARCH)
    manager.record_consent("session-2", ConsentType.IMPROVEMENT)
    manager.record_consent("session-3", ConsentType.RESEARCH)
    manager.withdraw_consent("session-3")

    stats = manager.get_consent_stats()

    assert stats == {
        "active_consents": 2,
        "withdrawn_consents": 1,
        "by_type": {
            "improvement": 1,
            "research": 1,
        },
    }


def test_record_consent_replaces_existing_session_and_clears_withdrawal(tmp_path):
    manager = ConsentManager(str(tmp_path / "users.db"))
    manager.record_consent("session-1", ConsentType.RESEARCH)
    manager.withdraw_consent("session-1")

    replaced = manager.record_consent("session-1", ConsentType.ANONYMOUS)

    assert replaced.consent_type is ConsentType.ANONYMOUS
    assert manager.has_valid_consent("session-1") is True
    assert manager.get_consent("session-1").withdrawn is False


def test_create_consent_manager_factory_returns_initialized_manager(tmp_path):
    manager = create_consent_manager(str(tmp_path / "factory.db"))

    assert isinstance(manager, ConsentManager)
    assert (tmp_path / "factory.db").exists()
