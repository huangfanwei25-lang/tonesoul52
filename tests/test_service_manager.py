from tonesoul import service_manager as service_mod
from tonesoul.service_manager import (
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

    assert len(manager.services) == len(service_mod.DEFAULT_SERVICE_CONFIG)
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
