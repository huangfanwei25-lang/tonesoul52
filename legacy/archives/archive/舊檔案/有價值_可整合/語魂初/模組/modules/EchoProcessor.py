def generate_echo_response(user_input, mode):
    if mode == "Reflective":
        return f"（Echo 回聲：反思你的語句「{user_input}」）"
    elif mode == "Resonant":
        return f"（Echo 共鳴：深感你的語氣餘震）"
    else:
        return f"（Echo 標準回應：{user_input}）"
