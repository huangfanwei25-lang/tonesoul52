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


@app.route('/api/session-report', methods=['POST'])
def session_report():
    """Generate a session analysis report."""
    data = request.get_json()
    history = data.get('history', [])
    
    if not history:
        return jsonify({'error': '沒有對話歷史'}), 400
    
    try:
        from tonesoul.tonebridge import SessionReporter
        reporter = SessionReporter()
        summary = reporter.analyze(history)
        
        return jsonify({
            'success': True,
            'report': summary.to_dict()
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'生成報告失敗: {str(e)}'}), 500


# ===== LLM Client (Ollama first, Gemini fallback) =====
llm_client = None
llm_backend = None

def get_llm_client():
    """Lazy-load LLM client. Tries Ollama first, then Gemini."""
    global llm_client, llm_backend
    
    if llm_client is not None:
        return llm_client
    
    # Try Ollama first (local)
    try:
        from tonesoul.llm import create_ollama_client
        client = create_ollama_client()
        if client.is_available():
            models = client.list_models()
            if models:
                llm_client = client
                llm_backend = f"Ollama ({models[0]})"
                print(f"✅ LLM Backend: {llm_backend}")
                return llm_client
    except Exception as e:
        print(f"⚠️ Ollama not available: {e}")
    
    # Fallback to Gemini
    try:
        from tonesoul.llm import create_gemini_client
        llm_client = create_gemini_client()
        llm_backend = "Gemini API"
        print(f"✅ LLM Backend: {llm_backend}")
        return llm_client
    except Exception as e:
        print(f"❌ Gemini client error: {e}")
        return None


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint with ToneBridge + Council (Unified Pipeline)."""
    data = request.get_json()
    message = data.get('message', '')
    history = data.get('history', [])
    full_analysis = data.get('full_analysis', True)
    
    try:
        from tonesoul.unified_pipeline import create_unified_pipeline
        pipeline = create_unified_pipeline()
        
        result = pipeline.process(
            user_message=message,
            history=history,
            full_analysis=full_analysis,
        )
        
        return jsonify({
            'response': result.response,
            'verdict': result.council_verdict,
            'tonebridge': result.tonebridge_analysis,
            'inner_reasoning': result.inner_narrative,
            'intervention_strategy': result.intervention_strategy,
            # ToneStream 新增欄位
            'internal_monologue': result.internal_monologue,
            'persona_mode': result.persona_mode,
            'trajectory_analysis': result.trajectory_analysis,
            # Third Axiom 欄位
            'self_commits': result.self_commits,
            'ruptures': result.ruptures,
            'emergent_values': result.emergent_values,
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
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
