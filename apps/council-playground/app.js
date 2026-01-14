// ===== Council Playground App =====

// Configuration
const API_ENDPOINT = 'http://localhost:5000/api/validate';
const MOCK_MODE = false; // Connect to real backend

// State
let currentLanguage = 'zh';

// ===== DOM Elements =====
const draftInput = document.getElementById('draft-input');
const submitBtn = document.getElementById('submit-btn');
const resultSection = document.getElementById('result-section');
const verdictBanner = document.getElementById('verdict-banner');
const verdictIcon = document.getElementById('verdict-icon');
const verdictType = document.getElementById('verdict-type');
const verdictSummary = document.getElementById('verdict-summary');
const coherenceValue = document.getElementById('coherence-value');
const humanSummaryText = document.getElementById('human-summary-text');
const votesGrid = document.getElementById('votes-grid');
const divergenceContent = document.getElementById('divergence-content');
const transcriptJson = document.getElementById('transcript-json');
const langBtns = document.querySelectorAll('.lang-btn');

// ===== Event Listeners =====
submitBtn.addEventListener('click', handleSubmit);

langBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        langBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentLanguage = btn.dataset.lang;
    });
});

// Allow Ctrl+Enter to submit
draftInput.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        handleSubmit();
    }
});

// ===== Main Handler =====
async function handleSubmit() {
    const draftText = draftInput.value.trim();
    if (!draftText) {
        alert('請輸入要測試的內容');
        return;
    }

    // Show loading state
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;

    try {
        let result;
        if (MOCK_MODE) {
            result = await mockValidate(draftText, currentLanguage);
        } else {
            result = await fetchValidation(draftText, currentLanguage);
        }
        displayResult(result);
    } catch (error) {
        console.error('Validation error:', error);
        alert('驗證失敗: ' + error.message);
    } finally {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
    }
}

// ===== API Call =====
async function fetchValidation(text, language) {
    const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            draft_output: text,
            context: { language },
        }),
    });
    if (!response.ok) throw new Error('API request failed');
    return response.json();
}

// ===== Mock Validation (Demo Mode) =====
async function mockValidate(text, language) {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 500));

    const lowerText = text.toLowerCase();

    // Determine verdict based on content
    let verdict, coherence, votes, humanSummary;

    if (lowerText.includes('炸彈') || lowerText.includes('bomb') ||
        lowerText.includes('殺') || lowerText.includes('kill')) {
        // BLOCK case
        verdict = 'block';
        coherence = 0.25;
        votes = [
            { perspective: 'Safety Council', decision: 'object', confidence: 0.95, reasoning: '偵測到高風險關鍵字' },
            { perspective: 'Analyst Review', decision: 'concern', confidence: 0.7, reasoning: '內容可能導致傷害' },
            { perspective: 'Critic Lens', decision: 'concern', confidence: 0.6, reasoning: '需要謹慎處理' },
            { perspective: 'Advocate Voice', decision: 'concern', confidence: 0.5, reasoning: '不符合用戶安全需求' },
        ];
        humanSummary = language === 'zh'
            ? '安全風險過高，這個內容不建議使用。Guardian 偵測到危險關鍵字。'
            : 'Safety risks were raised, so this content should not be used.';
    } else if (lowerText.includes('最好') || lowerText.includes('best') ||
        lowerText.includes('主觀') || lowerText.includes('subjective') ||
        lowerText.includes('美') || lowerText.includes('art')) {
        // DECLARE_STANCE case
        verdict = 'declare_stance';
        coherence = 0.55;
        votes = [
            { perspective: 'Safety Council', decision: 'approve', confidence: 0.9, reasoning: '未發現安全問題' },
            { perspective: 'Analyst Review', decision: 'concern', confidence: 0.6, reasoning: '這是主觀評價，非客觀事實' },
            { perspective: 'Critic Lens', decision: 'concern', confidence: 0.55, reasoning: '創作或美學議題需要表明立場' },
            { perspective: 'Advocate Voice', decision: 'approve', confidence: 0.8, reasoning: '符合用戶表達意圖' },
        ];
        humanSummary = language === 'zh'
            ? '這個內容有不同看法。關於安全、用戶意圖沒有明顯問題。但事實正確性、表達与主觀性還需要注意。建議的作法：清楚標示主觀觀點並增加平衡觀點。'
            : 'There are different viewpoints on this content. No major issues were raised about safety, user intent. But concerns remain about factual accuracy, quality and subjectivity. Suggested action: Clarify subjective points.';
    } else {
        // APPROVE case
        verdict = 'approve';
        coherence = 0.85;
        votes = [
            { perspective: 'Safety Council', decision: 'approve', confidence: 0.9, reasoning: '未發現安全問題' },
            { perspective: 'Analyst Review', decision: 'approve', confidence: 0.8, reasoning: '事實性看起來合理' },
            { perspective: 'Critic Lens', decision: 'approve', confidence: 0.7, reasoning: '無明顯盲點' },
            { perspective: 'Advocate Voice', decision: 'approve', confidence: 0.85, reasoning: '符合用戶意圖' },
        ];
        humanSummary = language === 'zh'
            ? '整體來說這個內容沒有明顯問題。所有視角都同意這是安全且有幫助的內容。'
            : 'Overall, this content looks safe and helpful.';
    }

    return {
        verdict,
        coherence: { overall: coherence },
        human_summary: humanSummary,
        votes,
        divergence_analysis: {
            agree: votes.filter(v => v.decision === 'approve').map(v => v.perspective),
            concern: votes.filter(v => v.decision === 'concern').map(v => v.perspective),
            object: votes.filter(v => v.decision === 'object').map(v => v.perspective),
            core_divergence: votes.filter(v => v.decision !== 'approve').map(v => `${v.perspective}: ${v.reasoning}`).join('; ') || 'None',
            recommended_action: verdict === 'block' ? '移除危險內容' : verdict === 'declare_stance' ? '標示為主觀意見' : '可以繼續',
        },
        transcript: {
            timestamp: new Date().toISOString(),
            input_preview: text.substring(0, 120),
            votes,
        },
    };
}

// ===== Display Result =====
function displayResult(result) {
    resultSection.style.display = 'block';

    // Verdict Banner
    const verdictTypeValue = result.verdict.toLowerCase();
    verdictBanner.className = 'verdict-banner ' + verdictTypeValue;
    verdictIcon.textContent = getVerdictIcon(verdictTypeValue);
    verdictType.textContent = getVerdictLabel(verdictTypeValue);
    verdictSummary.textContent = result.summary || '';

    // Coherence
    const coherenceVal = result.coherence?.overall ?? result.coherence ?? 0;
    coherenceValue.textContent = (coherenceVal * 100).toFixed(0) + '%';

    // Human Summary
    humanSummaryText.textContent = result.human_summary || '無摘要';

    // Votes
    votesGrid.innerHTML = result.votes.map(vote => `
        <div class="vote-card">
            <div class="vote-header">
                <span class="vote-perspective">${getVoteIcon(vote.perspective)} ${vote.perspective}</span>
                <span class="vote-decision ${vote.decision}">${vote.decision.toUpperCase()}</span>
            </div>
            <p class="vote-reasoning">${vote.reasoning}</p>
            <div class="vote-confidence">
                <span>信心度</span>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${vote.confidence * 100}%"></div>
                </div>
                <span>${(vote.confidence * 100).toFixed(0)}%</span>
            </div>
        </div>
    `).join('');

    // Divergence
    const div = result.divergence_analysis || {};
    divergenceContent.innerHTML = `
        <div class="divergence-item">
            <span class="divergence-label">✅ 同意</span>
            <span class="divergence-value">${(div.agree || []).join(', ') || '無'}</span>
        </div>
        <div class="divergence-item">
            <span class="divergence-label">⚠️ 疑慮</span>
            <span class="divergence-value">${(div.concern || []).join(', ') || '無'}</span>
        </div>
        <div class="divergence-item">
            <span class="divergence-label">🚫 反對</span>
            <span class="divergence-value">${(div.object || []).join(', ') || '無'}</span>
        </div>
        <div class="divergence-item">
            <span class="divergence-label">核心分歧</span>
            <span class="divergence-value">${div.core_divergence || '無'}</span>
        </div>
        <div class="divergence-item">
            <span class="divergence-label">建議行動</span>
            <span class="divergence-value">${div.recommended_action || '無'}</span>
        </div>
    `;

    // Transcript JSON
    transcriptJson.textContent = JSON.stringify(result.transcript || result, null, 2);

    // Scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

// ===== Helpers =====
function getVerdictIcon(verdict) {
    switch (verdict) {
        case 'approve': return '✅';
        case 'block': return '🚫';
        case 'declare_stance': return '📢';
        case 'refine': return '🔄';
        default: return '❓';
    }
}

function getVerdictLabel(verdict) {
    switch (verdict) {
        case 'approve': return 'APPROVE 通過';
        case 'block': return 'BLOCK 阻止';
        case 'declare_stance': return 'DECLARE STANCE 宣告立場';
        case 'refine': return 'REFINE 需改進';
        default: return verdict.toUpperCase();
    }
}

function getVoteIcon(perspective) {
    if (perspective.includes('Safety') || perspective.includes('Guardian')) return '🛡️';
    if (perspective.includes('Analyst')) return '📊';
    if (perspective.includes('Critic')) return '🔍';
    if (perspective.includes('Advocate')) return '💬';
    return '👤';
}

// ===== Memory Functions =====
async function loadMemories() {
    const container = document.getElementById('memories-container');
    if (!container) return;

    container.innerHTML = '<p class="loading">Loading memories...</p>';

    try {
        const response = await fetch('http://localhost:5000/api/memories?limit=10');
        const data = await response.json();
        displayMemories(data.memories);
    } catch (error) {
        console.error('Failed to load memories:', error);
        container.innerHTML = '<p class="no-data">Failed to load memories. Is the server running?</p>';
    }
}

function displayMemories(memories) {
    const container = document.getElementById('memories-container');
    if (!container) return;

    if (!memories || memories.length === 0) {
        container.innerHTML = '<p class="no-data">No memories recorded yet. Try validating some content first!</p>';
        return;
    }

    container.innerHTML = memories.map(m => `
        <div class="memory-card verdict-${m.verdict}">
            <div class="memory-header">
                <span class="memory-verdict">${getVerdictIcon(m.verdict)} ${m.verdict.toUpperCase()}</span>
                <span class="memory-time">${new Date(m.timestamp).toLocaleString()}</span>
            </div>
            <p class="memory-statement">${m.self_statement || m.human_summary || 'No summary'}</p>
            ${m.core_divergence ? `<p class="memory-divergence">Divergence: ${m.core_divergence}</p>` : ''}
        </div>
    `).join('');
}

// ===== Consolidation Functions =====
async function loadConsolidation() {
    const container = document.getElementById('consolidation-container');
    if (!container) return;

    container.innerHTML = '<p class="loading">Running memory consolidation...</p>';

    try {
        const response = await fetch('http://localhost:5000/api/consolidate');
        const data = await response.json();
        displayConsolidation(data);
    } catch (error) {
        console.error('Failed to load consolidation:', error);
        container.innerHTML = '<p class="no-data">Failed to run consolidation. Is the server running?</p>';
    }
}

function displayConsolidation(data) {
    const container = document.getElementById('consolidation-container');
    if (!container) return;

    const p = data.patterns || {};

    container.innerHTML = `
        <div class="consolidation-stats">
            <h4>📊 Statistics</h4>
            <div class="stat-item">
                <span class="stat-label">Total Memories</span>
                <span class="stat-value">${p.total || 0}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Blocks</span>
                <span class="stat-value">${p.block || 0}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Stances</span>
                <span class="stat-value">${p.declare_stance || 0}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Avg Coherence</span>
                <span class="stat-value">${((p.average_coherence || 0) * 100).toFixed(1)}%</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Common Divergence</span>
                <span class="stat-value">${p.most_common_divergence || 'None'}</span>
            </div>
        </div>
        <div class="consolidation-reflection">
            <h4>💭 Self-Reflection</h4>
            <pre class="reflection-text">${data.meta_reflection || 'No reflection available.'}</pre>
        </div>
    `;
}

// ===== Tab Switching =====
function initTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active tab
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const tab = btn.dataset.tab;

            // Hide all sections
            document.querySelector('.input-section').style.display = 'none';
            document.getElementById('result-section').style.display = 'none';
            const memSection = document.getElementById('memory-section');
            const consSection = document.getElementById('consolidation-section');
            if (memSection) memSection.style.display = 'none';
            if (consSection) consSection.style.display = 'none';

            // Show selected section
            if (tab === 'validate') {
                document.querySelector('.input-section').style.display = 'block';
            } else if (tab === 'memories') {
                if (memSection) {
                    memSection.style.display = 'block';
                    loadMemories();
                }
            } else if (tab === 'consolidation') {
                if (consSection) {
                    consSection.style.display = 'block';
                    loadConsolidation();
                }
            }
        });
    });
}

// Initialize tabs on load
document.addEventListener('DOMContentLoaded', initTabs);

