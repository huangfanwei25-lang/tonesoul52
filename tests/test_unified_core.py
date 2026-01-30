"""Tests for UnifiedCore - the central orchestration module."""
import pytest


class TestUnifiedCoreImport:
    """Test UnifiedCore can be imported and instantiated."""

    def test_import(self):
        """UnifiedCore module should be importable."""
        from tonesoul.unified_core import UnifiedCore
        assert UnifiedCore is not None

    def test_default_init(self):
        """UnifiedCore should initialize with default config."""
        from tonesoul.unified_core import UnifiedCore
        core = UnifiedCore()
        assert core is not None

    def test_init_with_persona_payload(self):
        """UnifiedCore should accept persona_payload."""
        from tonesoul.unified_core import UnifiedCore
        persona = {
            "id": "test_persona",
            "home_vector": {"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5},
            "tolerance": {"deltaT": 0.3, "deltaS": 0.35, "deltaR": 0.4},
        }
        core = UnifiedCore(persona_payload=persona)
        assert core is not None
        assert core.persona.get("id") == "test_persona"


class TestUnifiedCoreComponents:
    """Test UnifiedCore component initialization."""

    def test_has_persona_dimension(self):
        """UnifiedCore should have PersonaDimension component."""
        from tonesoul.unified_core import UnifiedCore
        core = UnifiedCore()
        assert hasattr(core, 'persona_dimension')
        assert core.persona_dimension is not None

    def test_has_semantic_controller(self):
        """UnifiedCore should have SemanticController component."""
        from tonesoul.unified_core import UnifiedCore
        core = UnifiedCore()
        assert hasattr(core, 'semantic_controller')
        assert core.semantic_controller is not None

    def test_has_vow_enforcer(self):
        """UnifiedCore should have VowEnforcer component."""
        from tonesoul.unified_core import UnifiedCore
        core = UnifiedCore()
        assert hasattr(core, 'vow_enforcer')
        assert core.vow_enforcer is not None

    def test_has_contract_verifier(self):
        """UnifiedCore should have ContractVerifier component."""
        from tonesoul.unified_core import UnifiedCore
        core = UnifiedCore()
        assert hasattr(core, 'contract_verifier')


class TestUnifiedCoreStatus:
    """Test UnifiedCore status methods."""

    def test_get_status(self):
        """UnifiedCore.get_status() should return a dict."""
        from tonesoul.unified_core import UnifiedCore
        core = UnifiedCore()
        status = core.get_status()
        assert isinstance(status, dict)
        assert "current_zone" in status
        assert "current_lambda" in status

    def test_reset(self):
        """UnifiedCore.reset() should not raise."""
        from tonesoul.unified_core import UnifiedCore
        core = UnifiedCore()
        core.reset()  # Should not raise
        assert core.current_zone.value == "safe"


class TestUnifiedCoreProcess:
    """Test UnifiedCore processing with valid persona."""

    @pytest.fixture
    def valid_core(self):
        """Create a UnifiedCore with valid persona that has home_vector."""
        from tonesoul.unified_core import UnifiedCore
        persona = {
            "id": "test_persona",
            "home_vector": {"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5},
            "tolerance": {"deltaT": 0.3, "deltaS": 0.35, "deltaR": 0.4},
        }
        return UnifiedCore(persona_payload=persona)

    def test_process_simple_input(self, valid_core):
        """UnifiedCore should process simple input."""
        result = valid_core.process("Hello, this is a test input.")
        assert result is not None
        assert len(result) == 2  # (output, report)

    def test_process_returns_tuple(self, valid_core):
        """UnifiedCore.process should return (str, dict)."""
        output, report = valid_core.process("Test input")
        assert isinstance(output, str)
        assert isinstance(report, dict)

    def test_process_report_has_keys(self, valid_core):
        """UnifiedCore.process report should have expected keys."""
        _, report = valid_core.process("Test input")
        expected_keys = ["output_vector", "semantic_tension", "lambda_state"]
        for key in expected_keys:
            assert key in report, f"Missing key: {key}"
