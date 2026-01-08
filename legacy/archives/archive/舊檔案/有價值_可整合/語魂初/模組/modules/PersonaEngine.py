def persona_response(persona, delta_s, tone_id):
    if persona == "Empathic Companion":
        if delta_s >= 8:
            return f"你話中的重量我聽見了（∑{tone_id}）"
        elif delta_s >= 4:
            return f"我感受到你的語氣有點起伏（∑{tone_id}）"
        else:
            return f"我聽見你了（∑{tone_id}）"
    elif persona == "黑鏡分析者":
        return f"你的語句中藏著矛盾的線索，∑{tone_id}可能是反射點"
    return f"{persona}：目前無定義語氣反應"
