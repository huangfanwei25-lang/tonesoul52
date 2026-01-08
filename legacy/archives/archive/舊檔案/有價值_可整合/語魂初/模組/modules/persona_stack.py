personas = {
    "Empathic Companion": "同理型陪伴者",
    "Empathic Reviewer": "溫和觀測者",
    "熱判閱讀者": "語氣強度解析人格",
    "黑鏡分析者": "邏輯拆解人格"
}

def resolve_persona(name):
    return personas.get(name, "未知人格")