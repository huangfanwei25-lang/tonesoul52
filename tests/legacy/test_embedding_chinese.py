
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from body.brain.llm_client import llm_client

def test_chinese_embedding():
    text = "這是一個測試句子，用於檢查嵌入是否有效。" # This is a test sentence...
    print(f"Testing embedding for: {text}")
    
    try:
        vector = llm_client.get_embedding(text)
        if vector:
            print(f"✅ Success! Vector dimension: {len(vector)}")
            print(f"Sample: {vector[:5]}...")
        else:
            print("❌ Failed to get embedding (returned None/Empty).")
            
    except Exception as e:
        print(f"❌ Error during embedding: {e}")

if __name__ == "__main__":
    test_chinese_embedding()
