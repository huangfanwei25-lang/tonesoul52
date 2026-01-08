import os
import shutil
import threading
import uuid
from pathlib import Path

from tonesoul52.memory_manager import write_seed


_BASE_TEMP = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "temp"))
os.makedirs(_BASE_TEMP, exist_ok=True)


def _make_temp_dir() -> Path:
    path = Path(_BASE_TEMP) / f"manual_{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def test_memory_manager_concurrent_writes() -> None:
    errors = []

    temp_root = _make_temp_dir()
    try:
        def worker(run_id: str) -> None:
            seed = {"run_id": run_id, "created_at": "2025-01-01T00:00:00Z"}
            try:
                write_seed(str(temp_root), run_id, seed)
            except Exception as exc:  # pragma: no cover - diagnostic for concurrency
                errors.append(exc)

        threads = [
            threading.Thread(target=worker, args=("run_a",)),
            threading.Thread(target=worker, args=("run_b",)),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert not errors
        assert (temp_root / "seeds" / "run_a.json").exists()
        assert (temp_root / "seeds" / "run_b.json").exists()
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
