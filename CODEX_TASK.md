# Codex Task: Full-Stack ToneSoul Demo

Create a complete working demo that connects the existing frontend to the Python backend.

---

## Task 1: Flask API Server

Create `apps/api/server.py`:

```python
"""
ToneSoul API Server
Connects frontend to PreOutputCouncil backend.
"""

import json
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tonesoul.council import PreOutputCouncil
from tonesoul.council.self_journal import load_recent_memory
from tonesoul.memory import consolidate

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

council = PreOutputCouncil()


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
    
    return jsonify(verdict.to_dict())


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
    print("Starting ToneSoul API Server...")
    print("Frontend: file:///apps/council-playground/index.html")
    print("API: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Dependencies**: Add `flask` and `flask-cors` to requirements or install:
```bash
pip install flask flask-cors
```

---

## Task 2: Update Frontend

Update `apps/council-playground/app.js`:

1. Change line 5:
```javascript
const MOCK_MODE = false; // Connect to real backend
```

2. Update `API_ENDPOINT` to:
```javascript
const API_ENDPOINT = 'http://localhost:5000/api/validate';
```

3. Add new functions at the end:
```javascript
// ===== Memory Functions =====
async function loadMemories() {
    try {
        const response = await fetch('http://localhost:5000/api/memories?limit=10');
        const data = await response.json();
        displayMemories(data.memories);
    } catch (error) {
        console.error('Failed to load memories:', error);
    }
}

function displayMemories(memories) {
    const container = document.getElementById('memories-container');
    if (!container) return;
    
    if (!memories || memories.length === 0) {
        container.innerHTML = '<p class="no-data">No memories recorded yet.</p>';
        return;
    }
    
    container.innerHTML = memories.map(m => `
        <div class="memory-card verdict-${m.verdict}">
            <div class="memory-header">
                <span class="memory-verdict">${m.verdict.toUpperCase()}</span>
                <span class="memory-time">${new Date(m.timestamp).toLocaleString()}</span>
            </div>
            <p class="memory-statement">${m.self_statement || m.human_summary}</p>
        </div>
    `).join('');
}

async function loadConsolidation() {
    try {
        const response = await fetch('http://localhost:5000/api/consolidate');
        const data = await response.json();
        displayConsolidation(data);
    } catch (error) {
        console.error('Failed to load consolidation:', error);
    }
}

function displayConsolidation(data) {
    const container = document.getElementById('consolidation-container');
    if (!container) return;
    
    container.innerHTML = `
        <div class="consolidation-stats">
            <h4>Statistics</h4>
            <p>Total memories: ${data.patterns.total}</p>
            <p>Blocks: ${data.patterns.block}</p>
            <p>Stances: ${data.patterns.declare_stance}</p>
            <p>Avg coherence: ${(data.patterns.average_coherence * 100).toFixed(1)}%</p>
        </div>
        <div class="consolidation-reflection">
            <h4>Self-Reflection</h4>
            <pre>${data.meta_reflection}</pre>
        </div>
    `;
}
```

---

## Task 3: Update HTML

Update `apps/council-playground/index.html`:

Add navigation tabs after header nav:
```html
<div class="tab-nav">
    <button class="tab-btn active" data-tab="validate">Validate</button>
    <button class="tab-btn" data-tab="memories">Memories</button>
    <button class="tab-btn" data-tab="consolidation">Consolidation</button>
</div>
```

Add memory and consolidation sections after result-section:
```html
<!-- Memory Section -->
<section class="memory-section" id="memory-section" style="display: none;">
    <h2 class="section-title">Self-Memory Journal</h2>
    <div id="memories-container" class="memories-container">
        <p class="loading">Loading memories...</p>
    </div>
</section>

<!-- Consolidation Section -->
<section class="consolidation-section" id="consolidation-section" style="display: none;">
    <h2 class="section-title">Memory Consolidation</h2>
    <div id="consolidation-container" class="consolidation-container">
        <p class="loading">Loading consolidation...</p>
    </div>
</section>
```

Add tab switching logic to app.js:
```javascript
// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        const tab = btn.dataset.tab;
        document.querySelectorAll('section').forEach(s => s.style.display = 'none');
        
        if (tab === 'validate') {
            document.getElementById('input-section').style.display = 'block';
            document.getElementById('result-section').style.display = 'none';
        } else if (tab === 'memories') {
            document.getElementById('memory-section').style.display = 'block';
            loadMemories();
        } else if (tab === 'consolidation') {
            document.getElementById('consolidation-section').style.display = 'block';
            loadConsolidation();
        }
    });
});
```

---

## Task 4: Add CSS for new sections

Add to `apps/council-playground/style.css`:
```css
/* Tab Navigation */
.tab-nav {
    display: flex;
    gap: var(--space-sm);
    padding: var(--space-md) var(--space-xl);
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
}

.tab-btn {
    padding: var(--space-sm) var(--space-lg);
    background: transparent;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-sm);
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s;
}

.tab-btn:hover {
    border-color: var(--accent-primary);
    color: var(--text-primary);
}

.tab-btn.active {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
    color: white;
}

/* Memory Cards */
.memories-container {
    display: flex;
    flex-direction: column;
    gap: var(--space-md);
}

.memory-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: var(--space-lg);
    border-left: 4px solid var(--text-muted);
}

.memory-card.verdict-block {
    border-left-color: var(--danger);
}

.memory-card.verdict-declare_stance {
    border-left-color: var(--warning);
}

.memory-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--space-sm);
}

.memory-verdict {
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
}

.memory-time {
    color: var(--text-muted);
    font-size: 12px;
}

.memory-statement {
    color: var(--text-secondary);
    line-height: 1.6;
}

/* Consolidation */
.consolidation-container {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: var(--space-lg);
}

.consolidation-stats,
.consolidation-reflection {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: var(--space-lg);
}

.consolidation-reflection pre {
    white-space: pre-wrap;
    color: var(--text-primary);
    line-height: 1.8;
}

.no-data, .loading {
    color: var(--text-muted);
    text-align: center;
    padding: var(--space-xl);
}
```

---

## Task 5: Create Startup Script

Create `run_demo.py` at project root:
```python
"""
ToneSoul Demo Launcher
Starts the API server and opens the browser.
"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def main():
    root = Path(__file__).parent
    api_path = root / "apps" / "api" / "server.py"
    frontend_path = root / "apps" / "council-playground" / "index.html"
    
    print("=" * 50)
    print("ToneSoul Demo")
    print("=" * 50)
    
    # Check dependencies
    try:
        import flask
        import flask_cors
    except ImportError:
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-cors", "-q"])
    
    # Start API server
    print("Starting API server...")
    server = subprocess.Popen([sys.executable, str(api_path)])
    
    # Wait for server to start
    time.sleep(2)
    
    # Open frontend
    print(f"Opening frontend: {frontend_path}")
    webbrowser.open(f"file:///{frontend_path}")
    
    print("\nPress Ctrl+C to stop the server")
    
    try:
        server.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.terminate()

if __name__ == "__main__":
    main()
```

---

## Verification

1. Run: `python run_demo.py`
2. Frontend should open in browser
3. Test validation with different inputs
4. Click "Memories" tab to see journal
5. Click "Consolidation" tab to see self-reflection

---

## Expected Result

A fully functional web demo where:
- User enters text
- Real PreOutputCouncil processes it
- Verdict, votes, and transcript displayed
- Memories tab shows self-journal entries
- Consolidation tab shows AI's self-reflection

**This proves ToneSoul works end-to-end.**
