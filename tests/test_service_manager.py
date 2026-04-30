from tonesoul import service_manager as service_mod
from tonesoul.service_manager import (
    DEFAULT_SERVICE_CONFIG,
    RESOURCE_CONFIGS,
    Priority,
    ResourceConfig,
    ResourceLevel,
    ServiceCode,
    ServiceManager,
    ServiceStatus,
)


def test_service_status_and_resource_config_to_dict():
    status = ServiceStatus(code=ServiceCode.TS001, priority=Priority.CRITICAL, enabled=False)
    config = ResourceConfig(level=ResourceLevel.STANDARD, model="qwen2.5:7b", memory_limit_gb=8)

    assert status.to_dict() == {
        "code": "TS001",
        "name": "Council",
        "priority": "CRITICAL",
        "enabled": False,
        "last_call": None,
        "call_count": 0,
        "error_count": 0,
    }
    assert config.to_dict() == {
        "level": "standard",
        "model": "qwen2.5:7b",
        "memory_limit_gb": 8,
        "gpu_layers": None,
    }


def test_service_manager_initializes_all_services_and_priority_order():
    manager = ServiceManager(ResourceLevel.STANDARD)

    ordered = manager.get_enabled_by_priority()

    assert len(manager.services) == len(DEFAULT_SERVICE_CONFIG)
    assert ordered[0].code is ServiceCode.TS001
    assert ordered[1].code is ServiceCode.TS002
    assert manager.get_model() == "qwen2.5:7b"


def test_record_call_updates_counts_and_last_call():
    manager = ServiceManager()

    manager.record_call(ServiceCode.TS003, success=True)
    manager.record_call(ServiceCode.TS003, success=False)

    status = manager.get_service(ServiceCode.TS003)
    assert status is not None
    assert status.call_count == 2
    assert status.error_count == 1
    assert status.last_call is not None


def test_status_report_contains_resource_config_and_services():
    manager = ServiceManager(ResourceLevel.ADVANCED)
    report = manager.get_status_report()

    assert report["resource_level"] == "advanced"
    assert report["resource_config"]["model"] == "qwen2.5:32b"
    assert report["services"]["TS007"]["name"] == "LLM"
    assert report["timestamp"]


def test_singleton_helpers_reuse_global_manager(monkeypatch):
    monkeypatch.setattr(service_mod, "_service_manager", None)

    first = service_mod.get_service_manager(ResourceLevel.ADVANCED)
    second = service_mod.get_service_manager(ResourceLevel.MINIMAL)
    service_mod.record_service_call(ServiceCode.TS001, success=True)

    assert first is second
    assert second.resource_level is ResourceLevel.ADVANCED
    assert second.get_service(ServiceCode.TS001).call_count == 1


# ─── Extended coverage ────────────────────────────────────────────────────────


class TestServiceCodeEnum:
    def test_all_seven_codes_present(self):
        codes = [c.name for c in ServiceCode]
        assert set(codes) == {"TS001", "TS002", "TS003", "TS004", "TS005", "TS006", "TS007"}

    def test_ts001_is_council(self):
        assert ServiceCode.TS001.value == "Council"

    def test_ts002_is_gate(self):
        assert ServiceCode.TS002.value == "Gate"


class TestPriorityEnum:
    def test_critical_higher_than_high(self):
        assert Priority.CRITICAL.value > Priority.HIGH.value

    def test_high_higher_than_normal(self):
        assert Priority.HIGH.value > Priority.NORMAL.value

    def test_normal_higher_than_low(self):
        assert Priority.NORMAL.value > Priority.LOW.value


class TestResourceConfigs:
    def test_all_three_levels_present(self):
        for level in ResourceLevel:
            assert level in RESOURCE_CONFIGS

    def test_advanced_has_highest_memory(self):
        advanced = RESOURCE_CONFIGS[ResourceLevel.ADVANCED]
        standard = RESOURCE_CONFIGS[ResourceLevel.STANDARD]
        minimal = RESOURCE_CONFIGS[ResourceLevel.MINIMAL]
        assert advanced.memory_limit_gb > standard.memory_limit_gb > minimal.memory_limit_gb

    def test_gpu_layers_set_for_non_minimal(self):
        assert RESOURCE_CONFIGS[ResourceLevel.STANDARD].gpu_layers is not None
        assert RESOURCE_CONFIGS[ResourceLevel.ADVANCED].gpu_layers is not None

    def test_minimal_gpu_layers_zero(self):
        assert RESOURCE_CONFIGS[ResourceLevel.MINIMAL].gpu_layers == 0


class TestServiceManager:
    def test_default_resource_level_is_minimal(self):
        manager = ServiceManager()
        assert manager.resource_level == ResourceLevel.MINIMAL

    def test_get_model_returns_correct_model(self):
        assert ServiceManager(ResourceLevel.MINIMAL).get_model() == "gemma3:4b"
        assert ServiceManager(ResourceLevel.STANDARD).get_model() == "qwen2.5:7b"

    def test_all_services_enabled_by_default(self):
        manager = ServiceManager()
        assert all(s.enabled for s in manager.services.values())

    def test_get_service_unknown_code_returns_none(self):
        manager = ServiceManager()
        # Non-existent key lookup: services is keyed by ServiceCode enum
        # Simulate by directly calling get with a plain string
        assert manager.get_service("nonexistent") is None  # type: ignore[arg-type]

    def test_record_call_on_missing_code_is_noop(self):
        manager = ServiceManager()
        # No error raised for a code not in services
        manager.record_call("bad_code")  # type: ignore[arg-type]

    def test_enabled_by_priority_sorted_descending(self):
        manager = ServiceManager()
        ordered = manager.get_enabled_by_priority()
        priorities = [s.priority.value for s in ordered]
        assert priorities == sorted(priorities, reverse=True)

    def test_disabled_service_excluded_from_priority_list(self):
        manager = ServiceManager()
        manager.services[ServiceCode.TS006].enabled = False
        enabled = manager.get_enabled_by_priority()
        codes = [s.code for s in enabled]
        assert ServiceCode.TS006 not in codes

    def test_status_report_has_all_service_codes(self):
        manager = ServiceManager()
        report = manager.get_status_report()
        for code in ServiceCode:
            assert code.name in report["services"]


class TestServiceStatusToDict:
    def test_call_count_reflected(self):
        status = ServiceStatus(code=ServiceCode.TS007, priority=Priority.HIGH)
        status.call_count = 5
        status.error_count = 2
        d = status.to_dict()
        assert d["call_count"] == 5
        assert d["error_count"] == 2

    def test_last_call_preserved(self):
        status = ServiceStatus(
            code=ServiceCode.TS001, priority=Priority.CRITICAL, last_call="2026-04-22T10:00:00"
        )
        assert status.to_dict()["last_call"] == "2026-04-22T10:00:00"


class TestResourceConfigToDict:
    def test_gpu_layers_included_when_set(self):
        config = ResourceConfig(
            level=ResourceLevel.ADVANCED,
            model="qwen2.5:32b",
            memory_limit_gb=32,
            gpu_layers=40,
        )
        assert config.to_dict()["gpu_layers"] == 40
