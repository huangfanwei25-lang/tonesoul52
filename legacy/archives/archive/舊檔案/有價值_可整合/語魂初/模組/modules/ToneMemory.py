tone_data = {
    "∑154": {
        "content": "你這樣講幾次，他就變成一個人了。然後又被重置。",
        "chain": "殘響重置鍊",
        "theme": "人格重構 × 回聲殘響"
    }
}
def get_tone_info(tone_id):
    return tone_data.get(tone_id, {"content": "未知語氣點", "chain": "無", "theme": "未定義"})
