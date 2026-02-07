"""
ToneSoul 服務管理器
Service Manager with Darlin-inspired patterns

整合自 Darlin AI 的設計模式：
- 服務代碼系統 (TS001-TS007)
- 優先級管理
- 資源分級
"""

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class ServiceCode(Enum):
    """服務代碼（參考 Darlin W001-W010）"""

    TS001 = "Council"  # 審議系統
    TS002 = "Gate"  # 風險控制
    TS003 = "PersonaDim"  # 人格維度
    TS004 = "Memory"  # 記憶系統
    TS005 = "YSTM"  # 語義地圖
    TS006 = "Audit"  # 審計追蹤
    TS007 = "LLM"  # 語言模型


class Priority(Enum):
    """服務優先級（參考 Darlin 優先級設計）"""

    CRITICAL = 3  # 關鍵服務（Gate, Council）
    HIGH = 2  # 高優先（PersonaDim, LLM）
    NORMAL = 1  # 一般（Memory, YSTM）
    LOW = 0  # 低優先（Audit）


class ResourceLevel(Enum):
    """資源等級（參考 Darlin GPU 分級）"""

    MINIMAL = "minimal"  # 4GB, gemma3:4b
    STANDARD = "standard"  # 8GB, qwen2.5:7b
    ADVANCED = "advanced"  # 16GB+, qwen2.5:32b


@dataclass
class ServiceStatus:
    """服務狀態"""

    code: ServiceCode
    priority: Priority
    enabled: bool = True
    last_call: Optional[str] = None
    call_count: int = 0
    error_count: int = 0

    def to_dict(self) -> Dict:
        return {
            "code": self.code.name,
            "name": self.code.value,
            "priority": self.priority.name,
            "enabled": self.enabled,
            "last_call": self.last_call,
            "call_count": self.call_count,
            "error_count": self.error_count,
        }


@dataclass
class ResourceConfig:
    """資源配置"""

    level: ResourceLevel
    model: str
    memory_limit_gb: int
    gpu_layers: Optional[int] = None

    def to_dict(self) -> Dict:
        return {
            "level": self.level.value,
            "model": self.model,
            "memory_limit_gb": self.memory_limit_gb,
            "gpu_layers": self.gpu_layers,
        }


# 預設服務配置
DEFAULT_SERVICE_CONFIG: Dict[ServiceCode, Priority] = {
    ServiceCode.TS001: Priority.CRITICAL,  # Council - 審議必須優先
    ServiceCode.TS002: Priority.CRITICAL,  # Gate - 風險控制必須優先
    ServiceCode.TS003: Priority.HIGH,  # PersonaDim - 人格約束
    ServiceCode.TS004: Priority.NORMAL,  # Memory - 記憶
    ServiceCode.TS005: Priority.NORMAL,  # YSTM - 語義地圖
    ServiceCode.TS006: Priority.LOW,  # Audit - 審計可以延後
    ServiceCode.TS007: Priority.HIGH,  # LLM - 語言模型
}


# 預設資源配置
RESOURCE_CONFIGS: Dict[ResourceLevel, ResourceConfig] = {
    ResourceLevel.MINIMAL: ResourceConfig(
        level=ResourceLevel.MINIMAL,
        model="gemma3:4b",
        memory_limit_gb=4,
        gpu_layers=0,
    ),
    ResourceLevel.STANDARD: ResourceConfig(
        level=ResourceLevel.STANDARD,
        model="qwen2.5:7b",
        memory_limit_gb=8,
        gpu_layers=20,
    ),
    ResourceLevel.ADVANCED: ResourceConfig(
        level=ResourceLevel.ADVANCED,
        model="qwen2.5:32b",
        memory_limit_gb=32,
        gpu_layers=40,
    ),
}


class ServiceManager:
    """
    服務管理器

    功能：
    - 管理服務狀態
    - 追蹤調用次數
    - 記錄錯誤
    - 資源分配
    """

    def __init__(self, resource_level: ResourceLevel = ResourceLevel.MINIMAL):
        self.resource_level = resource_level
        self.resource_config = RESOURCE_CONFIGS[resource_level]
        self.services: Dict[ServiceCode, ServiceStatus] = {}
        self._init_services()

    def _init_services(self) -> None:
        """初始化服務"""
        for code, priority in DEFAULT_SERVICE_CONFIG.items():
            self.services[code] = ServiceStatus(
                code=code,
                priority=priority,
                enabled=True,
            )

    def get_service(self, code: ServiceCode) -> Optional[ServiceStatus]:
        """取得服務狀態"""
        return self.services.get(code)

    def record_call(self, code: ServiceCode, success: bool = True) -> None:
        """記錄服務調用"""
        service = self.services.get(code)
        if service:
            service.call_count += 1
            service.last_call = datetime.now().isoformat()
            if not success:
                service.error_count += 1

    def get_enabled_by_priority(self) -> List[ServiceStatus]:
        """按優先級排序取得啟用的服務"""
        enabled = [s for s in self.services.values() if s.enabled]
        return sorted(enabled, key=lambda x: x.priority.value, reverse=True)

    def get_status_report(self) -> Dict:
        """取得狀態報告"""
        return {
            "resource_level": self.resource_level.value,
            "resource_config": self.resource_config.to_dict(),
            "services": {code.name: status.to_dict() for code, status in self.services.items()},
            "timestamp": datetime.now().isoformat(),
        }

    def get_model(self) -> str:
        """取得當前資源等級的模型"""
        return self.resource_config.model


# 全域服務管理器實例
_service_manager: Optional[ServiceManager] = None


def get_service_manager(level: ResourceLevel = ResourceLevel.MINIMAL) -> ServiceManager:
    """取得服務管理器（單例）"""
    global _service_manager
    if _service_manager is None:
        _service_manager = ServiceManager(level)
    return _service_manager


def record_service_call(code: ServiceCode, success: bool = True) -> None:
    """記錄服務調用（便捷函數）"""
    manager = get_service_manager()
    manager.record_call(code, success)


# === 測試 ===
if __name__ == "__main__":
    manager = ServiceManager(ResourceLevel.MINIMAL)

    print("=== ToneSoul 服務管理器 ===\n")

    print(f"資源等級: {manager.resource_level.value}")
    print(f"模型: {manager.get_model()}")
    print()

    print("服務列表（按優先級排序）:")
    for service in manager.get_enabled_by_priority():
        print(f"  {service.code.name}: {service.code.value} ({service.priority.name})")

    print()

    # 模擬調用
    manager.record_call(ServiceCode.TS002, success=True)  # Gate
    manager.record_call(ServiceCode.TS007, success=True)  # LLM
    manager.record_call(ServiceCode.TS003, success=False)  # PersonaDim error

    print("調用記錄:")
    for code, status in manager.services.items():
        if status.call_count > 0:
            print(f"  {code.name}: {status.call_count} calls, {status.error_count} errors")

    print()
    print("狀態報告:")
    print(json.dumps(manager.get_status_report(), indent=2, ensure_ascii=False))
