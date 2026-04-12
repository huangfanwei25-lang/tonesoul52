/**
 * ToneSoul HUD — reflexive frontend
 * Pure mirror: receives JSON, maps to DOM. No logic.
 */

let ws = null;
let currentTier = 0;

// ── WebSocket ──────────────────────────────────────────

function connect() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${proto}://${location.host}/ws`);

  ws.onopen = () => {
    document.getElementById('ws-dot').className = 'status-dot live';
    document.getElementById('ws-label').textContent = 'live';
  };

  ws.onclose = () => {
    document.getElementById('ws-dot').className = 'status-dot off';
    document.getElementById('ws-label').textContent = 'disconnected';
    setTimeout(connect, 3000);
  };

  ws.onerror = () => {
    document.getElementById('ws-dot').className = 'status-dot stale';
    document.getElementById('ws-label').textContent = 'error';
  };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      if (msg.data) render(msg.data);
    } catch (e) {
      console.error('parse error', e);
    }
  };
}

// ── Tier pull (REST) ───────────────────────────────────

async function pullTier(tier) {
  currentTier = tier;

  // Update button states
  document.querySelectorAll('.tier-btn').forEach((btn, i) => {
    btn.classList.toggle('active', i === tier);
  });

  try {
    const res = await fetch(`/api/tier/${tier}`);
    const data = await res.json();
    render(data);

    // Show raw JSON for tier 1/2
    const raw = document.getElementById('raw-json');
    if (tier > 0) {
      raw.style.display = 'block';
      raw.textContent = JSON.stringify(data, null, 2);
    } else {
      raw.style.display = 'none';
    }
  } catch (e) {
    console.error('tier pull failed', e);
  }
}

// ── Render ─────────────────────────────────────────────

function render(d) {
  // Diagnostic line
  setText('diag-line', d.compact_diagnostic || '—');

  // Backend / Aegis
  setText('backend-label', `backend: ${d.backend_mode || '—'}`);

  // Soul Integral from diagnostic line
  const siMatch = (d.compact_diagnostic || '').match(/SI=([\d.]+)/);
  const si = siMatch ? parseFloat(siMatch[1]) : 0;
  renderSI(si);

  // Vows + tensions from diagnostic
  const vowMatch = (d.compact_diagnostic || '').match(/vows=(\d+)/);
  const tensionMatch = (d.compact_diagnostic || '').match(/tensions=(\d+)/);
  const vowCount = vowMatch ? parseInt(vowMatch[1]) : 0;
  const tensionCount = tensionMatch ? parseInt(tensionMatch[1]) : 0;

  setText('vow-count', vowCount);
  setText('tension-count', tensionCount);

  // Tension bar (0-10 scale)
  const tensionPct = Math.min(100, tensionCount * 10);
  document.getElementById('tension-fill').style.width = tensionPct + '%';
  if (tensionPct > 60) {
    document.getElementById('tension-fill').style.background = 'var(--orange)';
  } else {
    document.getElementById('tension-fill').style.background = 'var(--accent)';
  }

  // Aegis
  const aegisMatch = (d.compact_diagnostic || '').match(/aegis=(\w+)/);
  setText('aegis-label', `aegis: ${aegisMatch ? aegisMatch[1] : '—'}`);

  // Session count from diagnostic
  const sessMatch = (d.compact_diagnostic || '').match(/sessions=(\d+)/);
  // fallback: not in compact_diagnostic for tier 0

  // Readiness
  const r = d.readiness || {};
  const badge = document.getElementById('readiness-badge');
  badge.textContent = (r.status || 'unknown').toUpperCase();
  badge.className = `readiness-badge ${r.status || 'unknown'}`;
  setText('readiness-detail', r.summary_text || '—');

  // Task track
  const tt = d.task_track_hint || {};
  setText('task-track', tt.suggested_track || '—');
  setText('task-track-detail', tt.summary_text || '—');

  // Deliberation mode
  const dm = d.deliberation_mode_hint || {};
  setText('delib-mode', dm.suggested_mode || '—');

  // Claim boundary
  if (d.claim_boundary) {
    setText('claim-tier', d.claim_boundary.current_tier || '—');
    setText('claim-note', d.claim_boundary.receiver_note || '—');
  }

  // Mutation preflight
  if (d.mutation_preflight) {
    const mp = d.mutation_preflight;
    setText('mutation-status', mp.summary_text || '—');
    const nf = mp.next_followup || {};
    setText('mutation-next', nf.target ? `next: ${nf.target} (${nf.classification || ''})` : '—');
  }

  // Consumer contract
  if (d.consumer_contract) {
    const cc = d.consumer_contract;
    setText('consumer-summary', cc.summary_text || '—');
    setText('consumer-guard', cc.top_misread_guard || '—');
  }

  // Soul band
  renderBand(si);

  // Vow list (only if we have canonical_center or similar)
  renderVowList(d);
}

function renderSI(si) {
  const circumference = 2 * Math.PI * 70; // 439.8
  const offset = circumference * (1 - Math.min(1, si));
  const arc = document.getElementById('si-arc');
  arc.style.strokeDashoffset = offset;

  // Color based on value
  if (si >= 0.8) arc.style.stroke = 'var(--green)';
  else if (si >= 0.5) arc.style.stroke = 'var(--accent)';
  else if (si >= 0.3) arc.style.stroke = 'var(--orange)';
  else arc.style.stroke = 'var(--red)';

  setText('si-value', si.toFixed(4));
}

function renderBand(si) {
  const segments = document.querySelectorAll('#soul-band .band-segment');
  const bands = ['serene', 'alert', 'strained', 'critical'];
  let level = 0;
  if (si < 0.3) level = 3;
  else if (si < 0.5) level = 2;
  else if (si < 0.7) level = 1;

  segments.forEach((seg, i) => {
    seg.className = 'band-segment';
    if (i <= level) {
      seg.classList.add('active', bands[i]);
    }
  });
}

function renderVowList(d) {
  const container = document.getElementById('vow-list');
  container.innerHTML = '';

  // Try to extract vow info from various tier levels
  let vows = [];

  // From canonical_center
  if (d.canonical_center && d.canonical_center.current_short_board) {
    const sb = d.canonical_center.current_short_board;
    if (sb.summary_text) {
      vows.push(sb.summary_text);
    }
  }

  // From next_pull recommendation
  if (d.next_pull && d.next_pull.receiver_rule) {
    vows.push(d.next_pull.receiver_rule);
  }

  if (vows.length === 0) {
    container.innerHTML = '<div class="card-sub">pull tier 1+ for details</div>';
    return;
  }

  vows.forEach(v => {
    const item = document.createElement('div');
    item.className = 'vow-item';
    item.innerHTML = `<span class="vow-dot"></span><span>${escapeHtml(v)}</span>`;
    container.appendChild(item);
  });
}

// ── Helpers ────────────────────────────────────────────

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function escapeHtml(s) {
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}

// ── Init ───────────────────────────────────────────────

connect();
pullCrystals();
pullPipeline();

// Poll crystal/pipeline every 30s (slower than tier 0)
setInterval(() => { pullCrystals(); pullPipeline(); }, 30000);


// ── Crystal + Pipeline panels ─────────────────────────

async function pullCrystals() {
  try {
    const res = await fetch('/api/crystals');
    const d = await res.json();
    if (d.error) return;
    setText('crystal-total', d.total_crystals || 0);
    setText('crystal-active', d.active_count || 0);
    setText('crystal-stale', d.stale_count || 0);
    setText('crystal-freshness', typeof d.mean_freshness === 'number'
      ? d.mean_freshness.toFixed(2) : '—');

    const list = document.getElementById('crystal-rules');
    if (!list) return;
    list.innerHTML = '';
    (d.top_rules || []).forEach(r => {
      const item = document.createElement('div');
      item.className = 'crystal-rule';
      const phase = r.phase || 'ice';
      item.innerHTML = `<span class="phase-tag ${phase}">${phase}</span>${escapeHtml(r.rule)}`;
      list.appendChild(item);
    });
  } catch (e) {
    console.error('crystals fetch failed', e);
  }
}

async function pullPipeline() {
  try {
    const res = await fetch('/api/pipeline');
    const d = await res.json();
    if (d.error) return;
    setText('digest-count', d.digest_count || 0);
    setText('journal-count', d.journal_entries || 0);
  } catch (e) {
    console.error('pipeline fetch failed', e);
  }
}
