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
    return jsonify({'status': 'ok', 'version': '0.5.0'})


if __name__ == '__main__':
    print("=" * 50)
    print("ToneSoul API Server")
    print("=" * 50)
    print("Frontend: http://localhost:5000")
    print("API: http://localhost:5000/api/validate")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
