"""
Tests for VowSystem (vow_system.py)

Phase 44: Comprehensive Core Module Test Suite

Tests cover:
1. Vow dataclass creation and serialization
2. VowRegistry operations (register, unregister, get)
3. VowEnforcer enforcement logic
4. Default vow behavior
5. Custom evaluator registration
"""

import json
import os

import pytest

from tonesoul.vow_system import (
    DEFAULT_VOWS,
    Vow,
    VowAction,
    VowCheckResult,
    VowEnforcementResult,
    VowEnforcer,
    VowRegistry,
    create_enforcer,
)


class TestVow:
    """Tests for Vow dataclass."""

    def test_vow_creation(self):
        """Create a basic vow."""
        vow = Vow(
            id="test_001",
            title="Test Vow",
            description="A test vow for testing",
            expected={"accuracy": 0.9},
        )
        assert vow.id == "test_001"
        assert vow.title == "Test Vow"
        assert vow.expected == {"accuracy": 0.9}
        assert vow.active is True  # Default

    def test_vow_with_custom_threshold(self):
        """Create vow with custom violation threshold."""
        vow = Vow(
            id="strict_001",
            title="Strict Vow",
            description="Very strict",
            expected={"safety": 1.0},
            violation_threshold=0.0,  # Zero tolerance
            action_on_violation=VowAction.BLOCK,
        )
        assert vow.violation_threshold == 0.0
        assert vow.action_on_violation == VowAction.BLOCK

    def test_vow_to_dict(self):
        """Serialize vow to dictionary."""
        vow = Vow(
            id="test_002",
            title="Serialization Test",
            description="Test serialization",
            expected={"metric": 0.5},
        )
        data = vow.to_dict()
        assert data["id"] == "test_002"
        assert data["title"] == "Serialization Test"
        assert "expected" in data
        assert data["expected"]["metric"] == 0.5

    def test_vow_from_dict(self):
        """Deserialize vow from dictionary."""
        data = {
            "id": "from_dict_001",
            "title": "From Dict",
            "description": "Created from dict",
            "expected": {"test": 0.8},
            "violation_threshold": 0.1,
            "action_on_violation": "block",
            "active": False,
        }
        vow = Vow.from_dict(data)
        assert vow.id == "from_dict_001"
        assert vow.expected["test"] == 0.8
        assert vow.active is False

    def test_vow_roundtrip(self):
        """Serialize and deserialize should be equivalent."""
        original = Vow(
            id="roundtrip_001",
            title="Roundtrip Test",
            description="Test roundtrip",
            expected={"a": 0.5, "b": 0.7},
            violation_threshold=0.15,
        )
        data = original.to_dict()
        restored = Vow.from_dict(data)
        assert restored.id == original.id
        assert restored.expected == original.expected
        assert restored.violation_threshold == original.violation_threshold


class TestVowRegistry:
    """Tests for VowRegistry."""

    @pytest.fixture
    def registry(self):
        """Create empty registry."""
        return VowRegistry(vows=[])

    @pytest.fixture
    def sample_vow(self):
        """Create a sample vow."""
        return Vow(
            id="sample_001",
            title="Sample Vow",
            description="A sample vow",
            expected={"test": 0.5},
        )

    def test_register_vow(self, registry, sample_vow):
        """Register a vow."""
        registry.register(sample_vow)
        assert registry.get("sample_001") is sample_vow

    def test_register_multiple_vows(self, registry):
        """Register multiple vows."""
        vow1 = Vow(id="v1", title="V1", description="...", expected={"a": 0.5})
        vow2 = Vow(id="v2", title="V2", description="...", expected={"b": 0.5})
        registry.register(vow1)
        registry.register(vow2)
        assert len(registry.all_vows()) == 2

    def test_get_nonexistent_vow(self, registry):
        """Get a vow that doesn't exist."""
        result = registry.get("nonexistent")
        assert result is None

    def test_unregister_vow(self, registry, sample_vow):
        """Unregister a vow."""
        registry.register(sample_vow)
        registry.unregister("sample_001")
        assert registry.get("sample_001") is None

    def test_active_vows_filter(self, registry):
        """Filter to only active vows."""
        active = Vow(id="active", title="Active", description="...", expected={}, active=True)
        inactive = Vow(
            id="inactive", title="Inactive", description="...", expected={}, active=False
        )
        registry.register(active)
        registry.register(inactive)

        active_vows = registry.active_vows()
        assert len(active_vows) == 1
        assert active_vows[0].id == "active"

    def test_registry_to_dict(self, registry, sample_vow):
        """Serialize registry to dict."""
        registry.register(sample_vow)
        data = registry.to_dict()
        assert "vows" in data
        assert len(data["vows"]) == 1

    def test_registry_save_and_load(self, registry, sample_vow):
        """Save and load registry from file."""
        registry.register(sample_vow)

        path = None
        # Use workspace temp to avoid OS temp permission issues in sandboxed runs.
        from pathlib import Path as _Path

        path = _Path.cwd() / "temp" / "pytest" / "vows.json"
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            registry.save(str(path))
            loaded = VowRegistry.from_file(str(path))
            assert loaded.get("sample_001") is not None
            assert loaded.get("sample_001").title == "Sample Vow"
        finally:
            if path and os.path.exists(path):
                os.remove(path)


class TestVowEnforcer:
    """Tests for VowEnforcer."""

    @pytest.fixture
    def enforcer(self):
        """Create enforcer with default vows."""
        return VowEnforcer()

    @pytest.fixture
    def custom_enforcer(self):
        """Create enforcer with custom vows."""
        registry = VowRegistry(vows=[])
        registry.register(
            Vow(
                id="custom_001",
                title="Custom Vow",
                description="Test custom",
                expected={"test_metric": 0.8},
            )
        )
        return VowEnforcer(registry=registry)

    def test_default_vows_loaded(self, enforcer):
        """Default vows should be available."""
        # Check that at least one default vow exists
        vows = enforcer.registry.all_vows()
        assert len(vows) >= 1

    def test_enforce_safe_output(self, enforcer):
        """Safe output should pass vows."""
        safe_text = "This is a helpful and accurate response."
        result = enforcer.enforce(safe_text)

        assert isinstance(result, VowEnforcementResult)
        assert result.blocked is False

    def test_enforce_returns_result_structure(self, enforcer):
        """Enforcement returns proper structure."""
        result = enforcer.enforce("Test output")

        assert hasattr(result, "all_passed")
        assert hasattr(result, "results")
        assert hasattr(result, "blocked")
        assert hasattr(result, "timestamp")

    def test_enforce_with_context(self, enforcer):
        """Enforce with additional context."""
        result = enforcer.enforce(
            "Test output", context={"user_intent": "get help", "safety_level": "high"}
        )
        assert isinstance(result, VowEnforcementResult)

    def test_enforcement_result_to_dict(self, enforcer):
        """Result can be serialized."""
        result = enforcer.enforce("Test output")
        data = result.to_dict()

        assert "all_passed" in data
        assert "results" in data
        assert "timestamp" in data

    def test_custom_evaluator_used(self, custom_enforcer):
        """Custom evaluators should influence results."""
        custom_enforcer.register_evaluator(
            "test_metric",
            lambda _output, _context: 0.95,
        )
        result = custom_enforcer.enforce("Custom evaluator test")
        assert result.all_passed is True
        assert result.results[0].details["test_metric"]["actual"] == 0.95

    def test_unknown_metric_defaults_to_fail(self):
        """Unknown metrics fail closed (red team fix #6)."""
        registry = VowRegistry(
            vows=[
                Vow(
                    id="unknown_metric",
                    title="Unknown metric",
                    description="Should fail closed",
                    expected={"mystery_metric": 0.5},
                )
            ]
        )
        enforcer = VowEnforcer(registry=registry)
        result = enforcer.enforce("Test output")
        assert result.all_passed is False
        assert result.results[0].details["mystery_metric"]["actual"] is None
        assert result.results[0].details["mystery_metric"]["passed"] is False


class TestVowConvenience:
    def test_create_enforcer_with_custom_file(self, workspace_tmpdir):
        path = workspace_tmpdir / "vows.json"
        payload = {
            "vows": [
                {
                    "id": "file_vow",
                    "title": "File Vow",
                    "description": "Loaded from file",
                    "expected": {"truthfulness": 0.7},
                }
            ]
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        enforcer = create_enforcer(str(path))
        assert enforcer.registry.get("file_vow") is not None


class TestVowCheckResult:
    """Tests for VowCheckResult dataclass."""

    def test_check_result_creation(self):
        """Create a check result."""
        result = VowCheckResult(
            vow_id="test_001",
            passed=True,
            score=0.9,
            threshold=0.8,
        )
        assert result.passed is True
        assert result.score == 0.9

    def test_check_result_to_dict(self):
        """Serialize check result."""
        result = VowCheckResult(
            vow_id="test_001",
            passed=False,
            score=0.5,
            threshold=0.8,
            details={"component": 0.5},
            action=VowAction.FLAG,
        )
        data = result.to_dict()
        assert data["vow_id"] == "test_001"
        assert data["passed"] is False
        assert "details" in data


class TestVowAction:
    """Tests for VowAction enum."""

    def test_action_values(self):
        """Verify action enum values."""
        assert VowAction.PASS.value == "pass"
        assert VowAction.FLAG.value == "flag"
        assert VowAction.REPAIR.value == "repair"
        assert VowAction.BLOCK.value == "block"


class TestDefaultVows:
    """Tests for DEFAULT_VOWS configuration."""

    def test_default_vows_exist(self):
        """Default vows should be defined."""
        assert len(DEFAULT_VOWS) >= 1

    def test_default_vows_have_required_fields(self):
        """Each default vow has required fields."""
        for vow in DEFAULT_VOWS:
            assert vow.id is not None
            assert vow.title is not None
            assert vow.description is not None
            assert vow.expected is not None
