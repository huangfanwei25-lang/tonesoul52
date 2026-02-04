"""
🎮 按鍵精靈 v2.1 (中文輸入修復版)
功能：每 10 分鐘自動輸入文字並按 Enter，或執行其他按鍵組合
新增：支援中文輸入（使用剪貼簿方式）

需要安裝：
  pip install pyautogui pyperclip
"""

import tkinter as tk
from tkinter import ttk
import time
import threading

# 嘗試導入 pyautogui（更可靠）
try:
    import pyautogui

    pyautogui.FAILSAFE = True  # 移動滑鼠到角落可以緊急停止
    USE_PYAUTOGUI = True
except ImportError:
    USE_PYAUTOGUI = False
    try:
        from pynput.keyboard import Key, Controller

        kb = Controller()
    except ImportError:
        print("❌ 請安裝 pyautogui 或 pynput:")
        print("   pip install pyautogui")
        exit(1)


class KeyMacro:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎮 按鍵精靈 v2")
        self.root.geometry("350x310")  # 增加高度以容納新欄位
        self.root.resizable(False, False)

        # 狀態
        self.running = False
        self.paused = False
        self.interval = 600  # 10 分鐘
        self.remaining = self.interval
        self.press_count = 0

        self.setup_ui()

    def setup_ui(self):
        # 標題
        title = ttk.Label(self.root, text="⌨️ Alt + Enter 自動按鍵", font=("Arial", 12, "bold"))
        title.pack(pady=10)

        # 模式顯示
        mode = "pyautogui" if USE_PYAUTOGUI else "pynput"
        mode_label = ttk.Label(self.root, text=f"模式: {mode}", font=("Arial", 9))
        mode_label.pack()

        # 倒數顯示
        self.countdown_var = tk.StringVar(value="等待開始...")
        countdown = ttk.Label(
            self.root, textvariable=self.countdown_var, font=("Arial", 20, "bold")
        )
        countdown.pack(pady=10)

        # 狀態顯示
        self.status_var = tk.StringVar(value="⏸️ 已停止")
        status = ttk.Label(self.root, textvariable=self.status_var, font=("Arial", 10))
        status.pack(pady=5)

        # 計數顯示
        self.count_var = tk.StringVar(value="已按次數: 0")
        count_label = ttk.Label(self.root, textvariable=self.count_var, font=("Arial", 9))
        count_label.pack()

        # 按鈕框架
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=15)

        # 開始按鈕
        self.start_btn = ttk.Button(btn_frame, text="▶️ 開始", command=self.start, width=8)
        self.start_btn.grid(row=0, column=0, padx=5)

        # 暫停按鈕
        self.pause_btn = ttk.Button(
            btn_frame, text="⏸️ 暫停", command=self.toggle_pause, width=8, state="disabled"
        )
        self.pause_btn.grid(row=0, column=1, padx=5)

        # 停止按鈕
        self.stop_btn = ttk.Button(
            btn_frame, text="⏹️ 停止", command=self.stop, width=8, state="disabled"
        )
        self.stop_btn.grid(row=0, column=2, padx=5)

        # 測試按鈕
        test_btn = ttk.Button(btn_frame, text="🧪 測試", command=self.test_press, width=8)
        test_btn.grid(row=1, column=1, padx=5, pady=5)

        # 間隔設定
        interval_frame = ttk.Frame(self.root)
        interval_frame.pack(pady=5)
        ttk.Label(interval_frame, text="間隔(分鐘):").grid(row=0, column=0)
        self.interval_var = tk.StringVar(value="10")
        interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=5)
        interval_entry.grid(row=0, column=1, padx=5)

        # 動作類型選擇
        action_frame = ttk.Frame(self.root)
        action_frame.pack(pady=5)
        ttk.Label(action_frame, text="按鍵動作:").grid(row=0, column=0)
        self.action_var = tk.StringVar(value="繼續+Enter")
        action_combo = ttk.Combobox(
            action_frame,
            textvariable=self.action_var,
            values=["繼續+Enter", "Alt+Enter", "Enter", "Space", "F5"],
            width=12,
            state="readonly",
        )
        action_combo.grid(row=0, column=1, padx=5)

        # 自訂文字輸入（當選擇「繼續+Enter」時可修改）
        text_frame = ttk.Frame(self.root)
        text_frame.pack(pady=5)
        ttk.Label(text_frame, text="輸入文字:").grid(row=0, column=0)
        self.text_var = tk.StringVar(value="繼續")
        text_entry = ttk.Entry(text_frame, textvariable=self.text_var, width=15)
        text_entry.grid(row=0, column=1, padx=5)

    def press_combo(self):
        """按下設定的按鍵組合"""
        try:
            action = self.action_var.get()

            if USE_PYAUTOGUI:
                # pyautogui 方式（更可靠）
                if action == "繼續+Enter":
                    # 使用剪貼簿方式輸入中文（更可靠）
                    text = self.text_var.get()
                    try:
                        import pyperclip

                        pyperclip.copy(text)
                        time.sleep(0.1)
                        pyautogui.hotkey("ctrl", "v")
                        time.sleep(0.1)
                        pyautogui.press("enter")
                    except ImportError:
                        # 如果沒有 pyperclip，嘗試直接輸入（只支援英文）
                        pyautogui.typewrite(text, interval=0.05)
                        time.sleep(0.1)
                        pyautogui.press("enter")
                elif action == "Alt+Enter":
                    pyautogui.hotkey("alt", "enter")
                elif action == "Enter":
                    pyautogui.press("enter")
                elif action == "Space":
                    pyautogui.press("space")
                elif action == "F5":
                    pyautogui.press("f5")
            else:
                # pynput 方式
                from pynput.keyboard import Key

                if action == "繼續+Enter":
                    # 使用剪貼簿方式輸入中文
                    text = self.text_var.get()
                    try:
                        import pyperclip

                        pyperclip.copy(text)
                        time.sleep(0.1)
                        # Ctrl+V 貼上
                        kb.press(Key.ctrl)
                        kb.press("v")
                        time.sleep(0.05)
                        kb.release("v")
                        kb.release(Key.ctrl)
                        time.sleep(0.1)
                        kb.press(Key.enter)
                        kb.release(Key.enter)
                    except ImportError:
                        # 無 pyperclip，直接輸入（可能不支援中文）
                        kb.type(text)
                        time.sleep(0.1)
                        kb.press(Key.enter)
                        kb.release(Key.enter)
                elif action == "Alt+Enter":
                    kb.press(Key.alt)
                    kb.press(Key.enter)
                    time.sleep(0.1)
                    kb.release(Key.enter)
                    kb.release(Key.alt)
                elif action == "Enter":
                    kb.press(Key.enter)
                    time.sleep(0.1)
                    kb.release(Key.enter)
                elif action == "Space":
                    kb.press(Key.space)
                    time.sleep(0.1)
                    kb.release(Key.space)
                elif action == "F5":
                    kb.press(Key.f5)
                    time.sleep(0.1)
                    kb.release(Key.f5)

            self.press_count += 1
            self.count_var.set(f"已按次數: {self.press_count}")
            self.status_var.set(f"✅ 已按下 {action} @ {time.strftime('%H:%M:%S')}")
            return True
        except Exception as e:
            self.status_var.set(f"❌ 錯誤: {str(e)[:30]}")
            return False

    def test_press(self):
        """測試按鍵"""
        action = self.action_var.get()
        self.status_var.set(f"🧪 3秒後按下 {action}...")
        self.root.update()
        time.sleep(3)
        if self.press_combo():
            self.status_var.set("✅ 測試成功！")

    def timer_loop(self):
        """定時器循環"""
        while self.running:
            if not self.paused:
                if self.remaining <= 0:
                    self.press_combo()
                    self.remaining = self.interval
                else:
                    self.remaining -= 1

                mins = self.remaining // 60
                secs = self.remaining % 60
                self.countdown_var.set(f"{mins:02d}:{secs:02d}")

            time.sleep(1)

    def start(self):
        """開始"""
        try:
            self.interval = int(self.interval_var.get()) * 60
        except:
            self.interval = 600

        self.remaining = self.interval
        self.running = True
        self.paused = False

        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")
        self.status_var.set("▶️ 運行中...")

        # 立即按一次
        self.press_combo()

        # 啟動線程
        thread = threading.Thread(target=self.timer_loop, daemon=True)
        thread.start()

    def toggle_pause(self):
        """暫停/繼續"""
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(text="▶️ 繼續")
            self.status_var.set("⏸️ 已暫停")
        else:
            self.pause_btn.config(text="⏸️ 暫停")
            self.status_var.set("▶️ 運行中...")

    def stop(self):
        """停止"""
        self.running = False
        self.paused = False

        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled", text="⏸️ 暫停")
        self.stop_btn.config(state="disabled")

        self.countdown_var.set("等待開始...")
        self.status_var.set("⏸️ 已停止")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    print("🎮 按鍵精靈 v2")
    print(f"   模式: {'pyautogui (推薦)' if USE_PYAUTOGUI else 'pynput'}")
    print("   提示: 移動滑鼠到螢幕角落可緊急停止")
    print()
    app = KeyMacro()
    app.run()
