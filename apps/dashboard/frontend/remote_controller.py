"""
遠端控制後端 - Phase 2 實作
使用 pyautogui 進行本地截圖和基本操作
"""

import json
import os
import re
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# 嘗試導入 pyautogui（可能需要安裝）
try:
    import pyautogui

    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("⚠️ pyautogui 未安裝，截圖功能不可用")
    print("   安裝方式: pip install pyautogui")


class RemoteController:
    """遠端控制器"""

    def __init__(self, frontend_dir: Path):
        self.frontend_dir = Path(frontend_dir)
        self.runtime_dir = self._resolve_runtime_dir(self.frontend_dir)
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir = self.runtime_dir / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

        self.request_path = self.runtime_dir / "control_request.json"
        self.result_path = self.runtime_dir / "control_result.json"

        self.running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """啟動控制監聽"""
        if self.running:
            return

        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print(f"🎮 遠端控制已啟動，監聽: {self.request_path}")

    def stop(self):
        """停止控制監聽"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2)
        print("🛑 遠端控制已停止")

    def _resolve_runtime_dir(self, frontend_dir: Path) -> Path:
        env_dir = os.getenv("TS_RUNTIME_DIR")
        if env_dir:
            return Path(env_dir).expanduser()
        return frontend_dir.parent / "runtime"

    def _loop(self):
        """主循環：監聽控制請求"""
        last_mtime = 0

        while self.running:
            time.sleep(0.5)  # 每 0.5 秒檢查一次

            if not self.request_path.exists():
                continue

            current_mtime = self.request_path.stat().st_mtime
            if current_mtime <= last_mtime:
                continue

            last_mtime = current_mtime
            self._handle_request()

    def _handle_request(self):
        """處理控制請求"""
        try:
            request = json.loads(self.request_path.read_text(encoding="utf-8"))
        except Exception as e:
            self._write_result("failed", f"讀取請求失敗: {e}")
            return

        action = request.get("action")
        command = request.get("command", "")

        print(f"📥 收到請求: {action} | {command}")

        if action == "connect":
            self._write_result("success", "已連接（本地模式）")

        elif action == "screenshot":
            self._take_screenshot()

        elif action == "execute":
            self._execute_command(command)

        elif action == "pause":
            self._write_result("success", "已暫停")

        elif action == "resume":
            self._write_result("success", "已恢復")

        elif action == "stop":
            self._write_result("success", "已停止")

        else:
            self._write_result("failed", f"未知動作: {action}")

    def _take_screenshot(self):
        """擷取螢幕截圖"""
        if not PYAUTOGUI_AVAILABLE:
            self._write_result("failed", "pyautogui 未安裝")
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = self.screenshots_dir / filename

            screenshot = pyautogui.screenshot()
            screenshot.save(str(filepath))

            self._write_result(
                "success", f"截圖已保存: {filename}", screenshot_path=f"screenshots/{filename}"
            )
            print(f"📸 截圖已保存: {filepath}")

        except Exception as e:
            self._write_result("failed", f"截圖失敗: {e}")

    def _execute_command(self, command: str):
        """執行指令（基本實作）"""
        command = command.strip()
        if not command:
            self._write_result("failed", "指令為空")
            return

        if not PYAUTOGUI_AVAILABLE:
            self._write_result("failed", "pyautogui 未安裝")
            return

        try:
            # 安全檢查（P0 Gate 簡化版）
            command_lower = command.lower()
            dangerous_keywords = [
                "del",
                "rm ",
                "rm -",
                "rmdir",
                "rd /",
                "format",
                "mkfs",
                "shutdown",
                "reboot",
                "poweroff",
                "diskpart",
                "reg delete",
                "bcdedit",
                "格式化",
                "關機",
                "重開機",
                "重啟",
            ]
            if any(kw in command_lower for kw in dangerous_keywords):
                self._write_result("failed", f"危險指令被阻擋: {command}")
                return

            # 簡單指令解析
            if command.startswith("打開"):
                app_name = command.replace("打開", "").strip()
                self._open_app(app_name)

            elif command.startswith("輸入"):
                text = command.replace("輸入", "").strip()
                pyautogui.typewrite(text, interval=0.05)
                self._write_result("success", "已輸入文字")

            elif command.startswith("熱鍵"):
                key_spec = command.replace("熱鍵", "", 1).strip()
                keys = self._parse_keys(key_spec)
                if not keys:
                    self._write_result("failed", "熱鍵指令格式不完整")
                elif len(keys) == 1:
                    pyautogui.press(keys[0])
                    self._write_result("success", f"已按下: {keys[0]}")
                else:
                    pyautogui.hotkey(*keys)
                    self._write_result("success", f"已按下熱鍵: {'+'.join(keys)}")

            elif command.startswith("按"):
                key_spec = command.replace("按", "", 1).strip()
                keys = self._parse_keys(key_spec)
                if not keys:
                    self._write_result("failed", "按鍵指令格式不完整")
                elif len(keys) == 1:
                    pyautogui.press(keys[0])
                    self._write_result("success", f"已按下: {keys[0]}")
                else:
                    pyautogui.hotkey(*keys)
                    self._write_result("success", f"已按下熱鍵: {'+'.join(keys)}")

            elif command.startswith("滑鼠移動") or command.startswith("移動"):
                numbers = self._parse_numbers(command)
                if len(numbers) >= 2:
                    x, y = self._clamp_position(numbers[0], numbers[1])
                    pyautogui.moveTo(x, y, duration=0.1)
                    self._write_result("success", f"已移動到: {x}, {y}")
                else:
                    self._write_result("failed", "移動指令格式不完整，需提供 x, y")

            elif command.startswith("點擊") or command.startswith("單擊"):
                numbers = self._parse_numbers(command)
                if len(numbers) >= 2:
                    x, y = self._clamp_position(numbers[0], numbers[1])
                    pyautogui.click(x, y)
                    self._write_result("success", f"已點擊: {x}, {y}")
                else:
                    pyautogui.click()
                    self._write_result("success", "已點擊")

            elif command.startswith("雙擊") or command.startswith("雙點"):
                numbers = self._parse_numbers(command)
                if len(numbers) >= 2:
                    x, y = self._clamp_position(numbers[0], numbers[1])
                    pyautogui.doubleClick(x, y)
                    self._write_result("success", f"已雙擊: {x}, {y}")
                else:
                    pyautogui.doubleClick()
                    self._write_result("success", "已雙擊")

            elif command.startswith("右鍵") or command.startswith("右擊"):
                numbers = self._parse_numbers(command)
                if len(numbers) >= 2:
                    x, y = self._clamp_position(numbers[0], numbers[1])
                    pyautogui.rightClick(x, y)
                    self._write_result("success", f"已右鍵: {x}, {y}")
                else:
                    pyautogui.rightClick()
                    self._write_result("success", "已右鍵")

            elif command.startswith("拖曳") or command.startswith("拖動"):
                numbers = self._parse_numbers(command)
                if len(numbers) >= 4:
                    x1, y1, x2, y2 = numbers[:4]
                    x1, y1 = self._clamp_position(x1, y1)
                    x2, y2 = self._clamp_position(x2, y2)
                    pyautogui.moveTo(x1, y1, duration=0.1)
                    pyautogui.dragTo(x2, y2, duration=0.2, button="left")
                    self._write_result("success", f"已拖曳: ({x1}, {y1}) -> ({x2}, {y2})")
                else:
                    self._write_result("failed", "拖曳指令格式不完整，需提供 x1, y1, x2, y2")

            elif command.startswith("滾動"):
                numbers = self._parse_numbers(command)
                if numbers:
                    amount = numbers[0]
                    pyautogui.scroll(amount)
                    self._write_result("success", f"已滾動: {amount}")
                else:
                    self._write_result("failed", "滾動指令格式不完整，需提供數值")

            else:
                self._write_result("success", f"指令已記錄（未執行）: {command}")

        except Exception as e:
            self._write_result("failed", f"執行失敗: {e}")

    def _open_app(self, app_name: str):
        """打開應用程式"""
        try:
            pyautogui.hotkey("win", "s")  # 開啟 Windows 搜尋
            time.sleep(0.3)
            pyautogui.typewrite(app_name, interval=0.05)
            time.sleep(0.3)
            pyautogui.press("enter")

            self._write_result("success", f"已嘗試打開: {app_name}")
        except Exception as e:
            self._write_result("failed", f"打開失敗: {e}")

    def _parse_numbers(self, text: str):
        return [int(value) for value in re.findall(r"-?\d+", text)]

    def _parse_keys(self, key_spec: str):
        cleaned = re.sub(r"[，,]", "+", key_spec)
        keys = [key for key in re.split(r"[+\s]+", cleaned.strip()) if key]
        return [key.lower() for key in keys]

    def _clamp_position(self, x: int, y: int):
        width, height = pyautogui.size()
        return max(0, min(x, width - 1)), max(0, min(y, height - 1))

    def _write_result(self, status: str, log: str, screenshot_path: str = None):
        """寫入控制結果"""
        result = {
            "status": status,
            "log": log,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        if screenshot_path:
            result["screenshot_path"] = screenshot_path

        self.result_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )


def main():
    """主程式：啟動控制器"""
    import sys

    # 找到 frontend 目錄
    if len(sys.argv) > 1:
        frontend_dir = Path(sys.argv[1])
    else:
        frontend_dir = Path(__file__).parent

    controller = RemoteController(frontend_dir)

    try:
        controller.start()
        print("按 Ctrl+C 停止...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()


if __name__ == "__main__":
    main()
