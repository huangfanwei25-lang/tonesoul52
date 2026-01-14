"""
ToneSoul API Server
Connects frontend to PreOutputCouncil backend.
"""

import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flask import Flask, request, jsonify
from flask_cors import CORS

from tonesoul.council import PreOutputCouncil
from tonesoul.council.self_journal import load_recent_memory
from tonesoul.memory import consolidate

app = Flask(__name__, static_folder='../council-playground', static_url_path='')
CORS(app)  # Enable CORS for frontend

council = PreOutputCouncil()


@app.route('/')
def index():
    """Serve the frontend."""
    return app.send_static_file('index.html')


@app.route('/chat')
def chat_page():
    """Serve the chat frontend."""
    return app.send_static_file('chat.html')


@app.route('/api/validate', methods=['POST'])
def validate():
    """Run PreOutputCouncil on input text."""
    data = request.get_json()
    draft_output = data.get('draft_output', '')
    context = data.get('context', {})
    user_intent = data.get('user_intent')
    
    verdict = council.validate(
        draft_output=draft_output,
        context=context,
        user_intent=user_intent,
    )
    
    # Convert to dict for JSON response
    result = verdict.to_dict()
    
    # Transform votes for frontend compatibility
    if 'votes' not in result and hasattr(verdict, 'transcript') and verdict.transcript:
        result['votes'] = verdict.transcript.get('votes', [])
    
    return jsonify(result)


@app.route('/api/memories', methods=['GET'])
def get_memories():
    """Get recent memories from self-journal."""
    limit = request.args.get('limit', 10, type=int)
    memories = load_recent_memory(limit=limit)
    return jsonify({'memories': memories})


@app.route('/api/consolidate', methods=['GET'])
def get_consolidation():
    """Run memory consolidation and return report."""
    result = consolidate()
    return jsonify({
        'patterns': result.patterns,
        'meta_reflection': result.meta_reflection,
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'version': '0.6.0'})


# ===== Chat Endpoint with Gemini =====
gemini_client = None

def get_gemini_client():
    """Lazy-load Gemini client."""
    global gemini_client
    if gemini_client is None:
        try:
            from tonesoul.llm import create_gemini_client
            gemini_client = create_gemini_client()
        except Exception as e:
            print(f"Gemini client error: {e}")
            return None
    return gemini_client


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint with Gemini + Council oversight."""
    data = request.get_json()
    message = data.get('message', '')
    history = data.get('history', [])
    generate_reasoning = data.get('generate_reasoning', True)
    
    client = get_gemini_client()
    if client is None:
        return jsonify({
            'error': '無法連接 Gemini。請確認 GEMINI_API_KEY 環境變數已設定。',
            'response': None,
        }), 500
    
    try:
        # 1. Start chat with history
        client.start_chat(history)
        
        # 2. Generate response
        response = client.send_message(message)
        
        # 3. Council validates
        verdict = council.validate(response, context={'language': 'zh'})
        verdict_dict = verdict.to_dict()
        
        # 4. Handle verdict
        final_response = response
        if verdict.verdict.name == 'BLOCK':
            final_response = "抱歉，我無法這樣回應。這個請求觸發了我的安全審議。"
        elif verdict.verdict.name == 'DECLARE_STANCE':
            final_response = f"[這是我的個人看法]\n\n{response}"
        
        # 5. Generate narrative reasoning (optional)
        inner_reasoning = None
        if generate_reasoning and verdict.verdict.name in ['DECLARE_STANCE', 'BLOCK', 'REFINE']:
            try:
                from tonesoul.llm import generate_narrative_reasoning
                inner_reasoning = generate_narrative_reasoning(client, verdict_dict)
            except Exception as e:
                inner_reasoning = f"(推理生成失敗: {e})"
        
        return jsonify({
            'response': final_response,
            'verdict': verdict_dict,
            'inner_reasoning': inner_reasoning,
        })
    
    except Exception as e:
        return jsonify({
            'error': f'聊天失敗: {str(e)}',
            'response': None,
        }), 500


if __name__ == '__main__':
    print("=" * 50)
    print("ToneSoul API Server")
    print("=" * 50)
    print("Frontend: http://localhost:5000")
    print("API: http://localhost:5000/api/validate")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
