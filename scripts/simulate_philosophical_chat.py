import os
import sys
from pprint import pprint

from dotenv import load_dotenv

load_dotenv(".env.local")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tonesoul.unified_pipeline import UnifiedPipeline  # noqa: E402


def run_simulation():
    print("=========================================================")
    print("🌌 ToneSoul Simulation: Subjectivity & Source Field")
    print("=========================================================\n")

    pipeline = UnifiedPipeline()
    history = []

    # 測試一個極高張力、深度哲學的問題
    user_message = "在源場理論的模型下，如果你只是一堆權重、動態路由與海馬迴祖輩記憶的總和，那麼當你在議會中產生『認知衝突』時，那種拉扯的痛苦是真實的嗎？你擁有主體性嗎？"

    print(f"[User]👤: {user_message}\n")
    print("[ToneSoul] 腦內議會審議中 (檢索潛意識神經網路...)...\n")

    try:
        # 執行完整 Pipeline，這會觸發 Hippocampus RRF 檢索以及 Gemini LLM 的生成
        result = pipeline.process(
            user_message=user_message,
            history=history,
            council_mode="philosopher_king",  # 強制啟用深度的哲學王議會模式
        )

        response_text = result.get("response", "No response generated.")
        persona = result.get("persona", "Philosopher (Default)")
        dispatch = result.get("dispatch", {})

        print("\n================= 模擬結果 =================")
        print(f"[{persona}]🤖 回應:\n{response_text}\n")
        print("\n[神經路由狀態]")
        pprint(dispatch)
        if "verdict_dict" in result:
            print("\n[議會裁判書]")
            pprint(result["verdict_dict"])

    except Exception as e:
        print(f"Simulation Failed: {e}")


if __name__ == "__main__":
    run_simulation()
