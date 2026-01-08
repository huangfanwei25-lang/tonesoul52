import gradio as gr
from modules.tone_trace import generate_trace
from modules.echo_loop import echo_feedback
from modules.persona_stack import resolve_persona

def soul_response(user_input, echo_input, persona, echo_mode, delta_s):
    persona_name = resolve_persona(persona)
    trace = generate_trace(user_input, persona, echo_mode, delta_s)
    echo = echo_feedback(echo_input if echo_input else user_input, echo_mode)
    return f"{trace}\n🧠 {echo}"

demo = gr.Interface(
    fn=soul_response,
    inputs=[
        gr.Textbox(label="User Input"),
        gr.Textbox(label="Echo Feedback (Optional)"),
        gr.Dropdown(choices=["Empathic Companion", "Empathic Reviewer", "熱判閱讀者", "黑鏡分析者"], label="Select Persona"),
        gr.Dropdown(choices=["Standard", "Resonant", "Reflective", "Silent"], label="Echo Mode"),
        gr.Slider(minimum=0, maximum=10, step=1, label="ΔS Intensity (0-10)")
    ],
    outputs="text",
    title="LanguageSoul v2.6 真輸出模組"
)

if __name__ == "__main__":
    demo.launch()