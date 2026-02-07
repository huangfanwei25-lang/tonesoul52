"""
Tests for TimeIsland (time_island.py)

Phase 44: Comprehensive Core Module Test Suite

Tests cover:
1. TimeIsland creation and lifecycle (draft → active → completed → archived)
2. Input/output recording
3. Changelog and intervention tracking
4. Resonance and drift measurements
5. Serialization (to_dict, from_dict, to_yaml)
6. TimeIslandManager operations
"""

import pytest

from tonesoul.time_island import (
    ChangelogEntry,
    IslandState,
    SourceTrace,
    TimeIsland,
    TimeIslandManager,
    create_island,
    wrap_in_island,
)


class TestIslandState:
    """Tests for IslandState enum."""

    def test_state_values(self):
        """Verify state enum values."""
        assert IslandState.DRAFT.value == "draft"
        assert IslandState.ACTIVE.value == "active"
        assert IslandState.COMPLETED.value == "completed"
        assert IslandState.ARCHIVED.value == "archived"


class TestSourceTrace:
    """Tests for SourceTrace dataclass."""

    def test_source_trace_creation(self):
        """Create a source trace."""
        trace = SourceTrace(kind="memory", ref="mem_001")
        assert trace.kind == "memory"
        assert trace.ref == "mem_001"
        assert trace.timestamp != ""  # Auto-generated

    def test_source_trace_to_dict(self):
        """Serialize source trace."""
        trace = SourceTrace(kind="file", ref="/path/to/doc.md")
        data = trace.to_dict()
        assert data["kind"] == "file"
        assert data["ref"] == "/path/to/doc.md"

    def test_source_trace_from_dict(self):
        """Deserialize source trace."""
        data = {"kind": "api", "ref": "api_endpoint", "timestamp": "2026-01-01T00:00:00"}
        trace = SourceTrace.from_dict(data)
        assert trace.kind == "api"
        assert trace.ref == "api_endpoint"


class TestChangelogEntry:
    """Tests for ChangelogEntry dataclass."""

    def test_changelog_entry_creation(self):
        """Create a changelog entry."""
        entry = ChangelogEntry(action="create", reason="Initial creation")
        assert entry.action == "create"
        assert entry.reason == "Initial creation"
        assert entry.actor == "system"  # Default
        assert entry.timestamp != ""  # Auto-generated

    def test_changelog_entry_with_actor(self):
        """Create changelog with custom actor."""
        entry = ChangelogEntry(action="modify", reason="User request", actor="user")
        assert entry.actor == "user"

    def test_changelog_entry_to_dict(self):
        """Serialize changelog entry."""
        entry = ChangelogEntry(action="update", reason="Test")
        data = entry.to_dict()
        assert "action" in data
        assert "reason" in data
        assert "timestamp" in data
        assert "actor" in data


class TestTimeIsland:
    """Tests for TimeIsland dataclass."""

    @pytest.fixture
    def island(self):
        """Create a basic island."""
        return TimeIsland.create(context="Test context for decision")

    def test_island_creation(self, island):
        """Create a time island."""
        assert island.id.startswith("TI-")
        assert island.bounded_context == "Test context for decision"
        assert island.state == IslandState.DRAFT

    def test_island_factory_create(self):
        """Use factory method to create island."""
        island = TimeIsland.create(context="Factory created")
        assert island.bounded_context == "Factory created"
        assert island.window_start != ""

    def test_island_custom_id(self):
        """Create island with custom ID."""
        island = TimeIsland.create(context="Custom ID", island_id="custom_001")
        assert island.id == "custom_001"

    def test_island_lifecycle_draft_to_active(self, island):
        """Transition from draft to active."""
        assert island.state == IslandState.DRAFT
        island.activate()
        assert island.state == IslandState.ACTIVE

    def test_island_lifecycle_active_to_completed(self, island):
        """Transition from active to completed."""
        island.activate()
        island.complete()
        assert island.state == IslandState.COMPLETED
        assert island.window_end != ""

    def test_island_lifecycle_archive(self, island):
        """Archive an island."""
        island.activate()
        island.complete()
        island.archive()
        assert island.state == IslandState.ARCHIVED

    def test_add_input(self, island):
        """Add input source to island."""
        island.add_input(kind="memory", ref="mem_123")
        assert len(island.inputs) == 1
        assert island.inputs[0].kind == "memory"
        assert island.inputs[0].ref == "mem_123"

    def test_add_output(self, island):
        """Add output reference to island."""
        island.add_output("output_file.md")
        assert len(island.outputs) == 1
        assert island.outputs[0] == "output_file.md"

    def test_add_changelog(self, island):
        """Add changelog entry."""
        island.add_changelog(action="test", reason="Testing changelog")
        assert len(island.changelog) >= 1
        # Find the test entry
        test_entries = [e for e in island.changelog if e.action == "test"]
        assert len(test_entries) == 1

    def test_record_intervention(self, island):
        """Record human intervention."""
        island.record_intervention("User requested change")
        assert island.human_interventions == 1
        assert any(
            entry.action == "human_intervention" and entry.reason == "User requested change"
            for entry in island.changelog
        )

    def test_update_resonance(self, island):
        """Update resonance signal."""
        island.update_resonance(value_fit=0.8, consensus=0.9, risk=0.1)
        assert island.resonance_signal["value_fit"] == 0.8
        assert island.resonance_signal["consensus"] == 0.9
        assert island.resonance_signal["risk"] == 0.1

    def test_update_drift(self, island):
        """Update drift measurement."""
        island.update_drift(0.15)
        assert island.drift_from_start == 0.15

    def test_hash_generation(self, island):
        """Generate island hash."""
        hash1 = island.hash()
        assert hash1 is not None
        assert len(hash1) > 0

        # Modify island and check hash changes
        island.add_output("new_output")
        hash2 = island.hash()
        assert hash1 != hash2

    def test_to_dict(self, island):
        """Serialize island to dictionary."""
        island.activate()
        island.add_input("doc", "doc_001")
        island.add_output("result.txt")

        data = island.to_dict()
        assert data["id"] == island.id
        assert data["bounded_context"] == island.bounded_context
        assert data["state"] == "active"
        assert "inputs" in data
        assert "outputs" in data

    def test_from_dict(self, island):
        """Deserialize island from dictionary."""
        island.activate()
        island.add_input("mem", "mem_001")
        data = island.to_dict()

        restored = TimeIsland.from_dict(data)
        assert restored.id == island.id
        assert restored.state == island.state
        assert len(restored.inputs) == 1

    def test_roundtrip(self, island):
        """Serialize and deserialize should preserve data."""
        island.activate()
        island.add_input("file", "/path/to/file")
        island.add_output("output.json")
        island.update_resonance(0.5, 0.6, 0.1)

        data = island.to_dict()
        restored = TimeIsland.from_dict(data)

        assert restored.id == island.id
        assert restored.bounded_context == island.bounded_context
        assert restored.resonance_signal == island.resonance_signal

    def test_to_yaml(self, island):
        """Serialize to YAML format."""
        island.activate()
        yaml_str = island.to_yaml()
        assert isinstance(yaml_str, str)
        assert island.id in yaml_str
        assert "bounded_context" in yaml_str


class TestTimeIslandManager:
    """Tests for TimeIslandManager."""

    @pytest.fixture
    def manager(self, workspace_tmpdir):
        """Create a manager with temp storage."""
        yield TimeIslandManager(storage_path=str(workspace_tmpdir / "islands.json"))

    def test_manager_creation(self, manager):
        """Create manager."""
        assert manager is not None
        assert len(manager.islands) == 0

    def test_create_island(self, manager):
        """Create island via manager."""
        island = manager.create_island("Test context")
        assert island is not None
        assert island.state == IslandState.ACTIVE
        assert manager.current_island == island

    def test_get_island(self, manager):
        """Get island by ID."""
        island = manager.create_island("Context 1")
        retrieved = manager.get_island(island.id)
        assert retrieved is island

    def test_get_nonexistent_island(self, manager):
        """Get island that doesn't exist."""
        result = manager.get_island("nonexistent_id")
        assert result is None

    def test_complete_current(self, manager):
        """Complete current island."""
        island1 = manager.create_island("First context")
        manager.complete_current()
        assert island1.state == IslandState.COMPLETED
        assert manager.current_island is None

    def test_list_islands(self, manager):
        """List all islands."""
        manager.create_island("Context 1")
        manager.complete_current()
        manager.create_island("Context 2")

        all_islands = manager.list_islands()
        assert len(all_islands) == 2

    def test_list_islands_by_state(self, manager):
        """List islands filtered by state."""
        manager.create_island("C1")
        manager.complete_current()
        manager.create_island("C2")

        completed = manager.list_islands(state=IslandState.COMPLETED)
        assert len(completed) == 1

        active = manager.list_islands(state=IslandState.ACTIVE)
        assert len(active) == 1

    def test_save_and_load(self, workspace_tmpdir):
        """Save and load manager state."""
        path = workspace_tmpdir / "islands.json"

        # Create and save
        manager1 = TimeIslandManager(storage_path=str(path))
        island = manager1.create_island("Persistence test")
        island_id = island.id
        manager1.save()

        # Load in new manager
        manager2 = TimeIslandManager(storage_path=str(path))
        manager2.load()

        loaded = manager2.get_island(island_id)
        assert loaded is not None
        assert loaded.bounded_context == "Persistence test"

    def test_save_without_path_raises(self):
        manager = TimeIslandManager()
        with pytest.raises(ValueError):
            manager.save()

    def test_load_missing_path_noop(self, workspace_tmpdir):
        manager = TimeIslandManager()
        missing_path = workspace_tmpdir / "missing.json"
        manager.load(str(missing_path))
        assert manager.islands == {}
        assert manager.current_island is None


class TestTimeIslandConvenience:
    def test_create_island_defaults(self):
        island = create_island("quick context")
        assert island.state == IslandState.DRAFT
        assert island.window_start

    def test_wrap_in_island_success(self):
        def _work():
            return "ok"

        result, island = wrap_in_island("wrap test", _work)
        assert result == "ok"
        assert island.state == IslandState.COMPLETED
        assert "function_result:str" in island.outputs
        assert island.window_end
