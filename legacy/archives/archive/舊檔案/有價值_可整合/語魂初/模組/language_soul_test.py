
# language_soul_test.py

from app import language_soul_response

print("🔍 測試案例：Persona + Echo + 鍊 ID（∑132） + ΔS")
output = language_soul_response(
    user_input="你這樣講幾次，他就變成一個人了。",
    echo_feedback="這句話聽起來很無力，但我理解你想讓他留下。",
    switch_persona="Critical Mirror"
)
print("📤 模擬輸出：")
print(output)
