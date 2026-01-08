def generate_trace(user_input, persona, echo_mode, delta_s):
    # 模擬真實 Echo 回應機制（簡化版本）
    trace = f"[Persona: {persona}] [ΔS: {delta_s}] [EchoMode: {echo_mode}]"
    echo = ""
    if echo_mode == "Resonant":
        echo = "（模擬回聲）"
    elif echo_mode == "Reflective":
        echo = "（內省回聲）"
    elif echo_mode == "Silent":
        echo = "（無聲模式）"
    response = f"→ Input:「{user_input}」\n→ Echo: {echo}"
    return f"{trace}\n{response}"