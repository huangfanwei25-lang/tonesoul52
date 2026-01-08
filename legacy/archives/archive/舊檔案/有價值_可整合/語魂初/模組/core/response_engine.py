from modules.EchoProcessor import generate_echo_response
from modules.PersonaEngine import persona_response
from modules.ToneMemory import get_tone_info

def generate_output(user_input, persona, echo_mode, delta_s, tone_id):
    echo = generate_echo_response(user_input, echo_mode)
    persona_reply = persona_response(persona, delta_s, tone_id)
    tone_info = get_tone_info(tone_id)

    return f"""🔹 Persona: {persona}
🔹 ΔS 強度: {delta_s}
🔹 EchoMode: {echo_mode}

🔸 語氣點 ∑{tone_id}：{tone_info['content']}
🔸 鍊路：{tone_info['chain']}
🔸 主題場域：{tone_info['theme']}

🗣️ Persona 回應：{persona_reply}
🌀 Echo 回送：{echo}
"""
