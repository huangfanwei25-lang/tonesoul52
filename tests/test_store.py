from __future__ import annotations

from pathlib import Path

from tonesoul import store as store_module
from tonesoul.backends.file_store import FileStore


def setup_function() -> None:
    store_module.reset_store()


def teardown_function() -> None:
    store_module.reset_store()


def test_force_file_store_env_skips_redis(monkeypatch) -> None:
    monkeypatch.setenv("TONESOUL_FORCE_FILE_STORE", "1")

    def _unexpected_try_redis(url: str):
        raise AssertionError(f"_try_redis should not run when force-file env is set: {url}")

    monkeypatch.setattr(store_module, "_try_redis", _unexpected_try_redis)

    store = store_module.get_store()

    assert isinstance(store, FileStore)
    assert store.backend_name == "file"


def test_disabled_redis_url_env_skips_redis(monkeypatch) -> None:
    monkeypatch.delenv("TONESOUL_FORCE_FILE_STORE", raising=False)
    monkeypatch.setenv("TONESOUL_REDIS_URL", "off")

    def _unexpected_try_redis(url: str):
        raise AssertionError(f"_try_redis should not run when redis url is disabled: {url}")

    monkeypatch.setattr(store_module, "_try_redis", _unexpected_try_redis)

    store = store_module.get_store()

    assert isinstance(store, FileStore)
    assert store.backend_name == "file"


def test_disabled_redis_url_argument_skips_redis(monkeypatch) -> None:
    monkeypatch.delenv("TONESOUL_FORCE_FILE_STORE", raising=False)
    monkeypatch.delenv("TONESOUL_REDIS_URL", raising=False)

    def _unexpected_try_redis(url: str):
        raise AssertionError(
            f"_try_redis should not run when redis url argument is disabled: {url}"
        )

    monkeypatch.setattr(store_module, "_try_redis", _unexpected_try_redis)

    store = store_module.get_store(redis_url="none")

    assert isinstance(store, FileStore)
    assert store.backend_name == "file"


def test_file_store_get_state_ignores_corrupt_json(tmp_path: Path, capsys) -> None:
    state_path = tmp_path / "governance_state.json"
    state_path.write_text("{not-json", encoding="utf-8")

    store = FileStore(gov_path=state_path)

    assert store.get_state() == {}
    assert "Ignoring corrupt JSON store file" in capsys.readouterr().err
