def echo_feedback(user_input, mode):
    if mode == "Resonant":
        return f"Echo 回送：感受到你的情緒了：{user_input}"
    elif mode == "Reflective":
        return f"Echo 反思：這句話引發了什麼？{user_input}"
    elif mode == "Silent":
        return f"Echo 靜默：...（沉默中）"
    else:
        return "Echo 模式錯誤"