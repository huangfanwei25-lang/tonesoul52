import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from memory.observer import MemoryObserver
from tonesoul.memory.soul_db import SqliteSoulDB


def test_dual_stream():
    print("🔍 Starting Dual-stream Memory Smoke Test...")

    # Use a temporary test database
    test_db_path = Path("memory/.tmp_tests/test_dual_stream.db")
    test_db_path.parent.mkdir(parents=True, exist_ok=True)
    if test_db_path.exists():
        test_db_path.unlink()

    db = SqliteSoulDB(db_path=test_db_path)
    observer = MemoryObserver(soul_db=db)

    # 1. Log a 'raw' action (Immutable stream)
    print("📝 Logging Raw Action...")
    observer.log_action(action="raw_test_action", params={"p": 1}, stream="raw")

    # 2. Log a 'curated' action (Processed knowledge)
    print("💎 Logging Curated Action...")
    observer.log_action(
        action="curated_test_fact",
        params={"f": "fact_001"},
        stream="curated",
        metadata={"confidence": 0.95},
    )

    # 3. Query 'raw' stream
    observer.query(limit=10)  # default should return all if not specified, but here we check stream
    # Actually, observer.query calls query_action_logs.
    # Let's check filtered query.

    print("🔎 Querying Streams...")
    all_raw = db.query_action_logs(stream="raw")
    all_curated = db.query_action_logs(stream="curated")

    print(f"✅ Raw logs count: {len(all_raw)}")
    print(f"✅ Curated logs count: {len(all_curated)}")

    assert len(all_raw) == 1
    assert len(all_curated) == 1
    assert all_curated[0]["stream"] == "curated"
    assert all_curated[0]["metadata"]["confidence"] == 0.95

    print("\n✨ Dual-stream Memory Smoke Test PASSED!")

    # Cleanup
    # test_db_path.unlink()


if __name__ == "__main__":
    test_dual_stream()
