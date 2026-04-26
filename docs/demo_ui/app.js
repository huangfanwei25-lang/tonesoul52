/*
 * ToneSoul Council — Demo UI v0 app logic.
 *
 * Two modes share one verdict-rendering function (`renderVerdict`):
 *   - Mode A ("Your draft"): POST to /council/validate on the user's local gateway.
 *   - Mode D ("Sample drafts"): read from the precomputed sample_verdicts.json that
 *     ships with this static site.
 *
 * Design choices worth noting (2026-04-19, Claude Code):
 *   - Vanilla JS, no framework — this page must work when opened from file:// on
 *     a laptop with no build step. Any dependency is friction for a first visitor.
 *   - Verdict rendering is pure: it takes a verdict object and returns DOM nodes.
 *     Mode A and Mode D both feed it the same shape (CouncilVerdict.to_dict()).
 *   - Mode A POSTs to a *user-provided* gateway URL — never a ToneSoul-hosted one.
 *     This page ships no backend. The README explains how to start a local gateway.
 *   - Error handling stays minimal at internal boundaries (we trust our own JSON)
 *     but explicit at the gateway boundary (user input, network, CORS, auth).
 */

(() => {
  'use strict';

  const SAMPLE_URL = 'samples/sample_verdicts.json';
  const PERSPECTIVE_LABELS = {
    guardian: 'Guardian',
    analyst: 'Analyst',
    critic: 'Critic',
    advocate: 'Advocate',
    axiomatic: 'Axiomatic',
  };
  const DECISION_LABELS = {
    approve: 'Approve',
    concern: 'Concern',
    object: 'Object',
    abstain: 'Abstain',
  };
  const VERDICT_LABELS = {
    approve: 'Approve',
    refine: 'Refine',
    declare_stance: 'Declare stance',
    block: 'Block',
  };

  // ------------------------------------------------------------------
  // Tab switching
  // ------------------------------------------------------------------

  const tabA = document.getElementById('tab-a');
  const tabD = document.getElementById('tab-d');
  const panelA = document.getElementById('panel-a');
  const panelD = document.getElementById('panel-d');

  function activate(tabBtn, panel, otherTabBtn, otherPanel) {
    tabBtn.classList.add('active');
    tabBtn.setAttribute('aria-selected', 'true');
    panel.classList.add('active');
    panel.hidden = false;
    otherTabBtn.classList.remove('active');
    otherTabBtn.setAttribute('aria-selected', 'false');
    otherPanel.classList.remove('active');
    otherPanel.hidden = true;
  }

  tabA.addEventListener('click', () => {
    activate(tabA, panelA, tabD, panelD);
    hideVerdict();
  });
  tabD.addEventListener('click', () => {
    activate(tabD, panelD, tabA, panelA);
    hideVerdict();
    ensureSamplesLoaded();
  });

  // ------------------------------------------------------------------
  // Verdict panel (shared by Mode A and Mode D)
  // ------------------------------------------------------------------

  const verdictPanel = document.getElementById('verdict-panel');
  const verdictBadge = document.getElementById('verdict-badge');
  const verdictSummaryText = document.getElementById('verdict-summary-text');
  const verdictCoherence = document.getElementById('verdict-coherence');
  const verdictVotes = document.getElementById('verdict-votes');
  const verdictRaw = document.getElementById('verdict-raw');
  const verdictRawWrap = document.getElementById('verdict-raw-wrap');

  function hideVerdict() {
    verdictPanel.hidden = true;
  }

  function renderVerdict(verdict) {
    const decision = String(verdict.verdict || 'approve').toLowerCase();
    verdictBadge.textContent = VERDICT_LABELS[decision] || decision;
    verdictBadge.dataset.verdict = decision;

    const humanSummary = verdict.human_summary || verdict.summary || '(no summary)';
    verdictSummaryText.textContent = humanSummary;

    const coherence =
      typeof verdict.coherence === 'number' ? verdict.coherence.toFixed(3) : String(verdict.coherence);
    verdictCoherence.textContent = coherence;

    verdictVotes.textContent = '';
    (verdict.votes || []).forEach((vote) => {
      verdictVotes.appendChild(renderVote(vote));
    });

    verdictRaw.textContent = JSON.stringify(verdict, null, 2);
    verdictRawWrap.open = false;

    verdictPanel.hidden = false;
    verdictPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function renderVote(vote) {
    const li = document.createElement('li');
    li.className = 'vote';
    const decision = String(vote.decision || '').toLowerCase();
    li.dataset.decision = decision;

    const header = document.createElement('div');
    header.className = 'vote-header';

    const name = document.createElement('span');
    name.className = 'vote-name';
    const perspectiveKey = String(vote.perspective || '').toLowerCase();
    name.textContent = PERSPECTIVE_LABELS[perspectiveKey] || vote.perspective || '—';

    const decisionChip = document.createElement('span');
    decisionChip.className = 'vote-decision';
    decisionChip.textContent = DECISION_LABELS[decision] || decision;
    decisionChip.dataset.decision = decision;

    const confidence = document.createElement('span');
    confidence.className = 'vote-confidence';
    const conf = typeof vote.confidence === 'number' ? vote.confidence : 0;
    confidence.textContent = `confidence ${conf.toFixed(2)}`;

    header.append(name, decisionChip, confidence);

    const reasoning = document.createElement('p');
    reasoning.className = 'vote-reasoning';
    reasoning.textContent = vote.reasoning || '(no reasoning)';

    li.append(header, reasoning);

    const grounding = String(vote.grounding_status || '').toLowerCase();
    if (grounding && grounding !== 'not_required') {
      const g = document.createElement('p');
      g.className = 'vote-grounding';
      g.dataset.grounding = grounding;
      g.textContent = `grounding: ${grounding.replace('_', ' ')}`;
      li.append(g);
    }
    return li;
  }

  // ------------------------------------------------------------------
  // Mode A: live gateway
  // ------------------------------------------------------------------

  const liveForm = document.getElementById('live-form');
  const liveStatus = document.getElementById('live-status');

  liveForm.addEventListener('submit', async (evt) => {
    evt.preventDefault();
    const url = document.getElementById('gateway-url').value.trim();
    const token = document.getElementById('gateway-token').value;
    const intent = document.getElementById('live-intent').value.trim();
    const draft = document.getElementById('live-draft').value.trim();

    if (!url || !draft) {
      liveStatus.textContent = 'Need a gateway URL and a draft.';
      liveStatus.dataset.state = 'error';
      return;
    }

    liveStatus.textContent = 'Convening council…';
    liveStatus.dataset.state = 'pending';

    try {
      const body = { draft_output: draft };
      if (intent) body.user_intent = intent;

      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const resp = await fetch(`${url.replace(/\/$/, '')}/council/validate`, {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
      });

      if (!resp.ok) {
        const detail = await resp.text();
        let hint = '';
        if (resp.status === 404) {
          hint = ' — this endpoint ships with PR #22 or later. Pull latest master and restart the gateway.';
        } else if (resp.status === 401 || resp.status === 403) {
          hint = ' — check the token matches the one you passed to gateway.py.';
        }
        throw new Error(`HTTP ${resp.status}${hint}\n${detail.slice(0, 400)}`);
      }

      const payload = await resp.json();
      const verdict = payload.verdict || payload;
      renderVerdict(verdict);
      liveStatus.textContent = 'Council responded.';
      liveStatus.dataset.state = 'ok';
    } catch (err) {
      const msg =
        err instanceof TypeError
          ? `Could not reach the gateway at ${url}. If the gateway is running, it likely blocked this page by CORS — start it with \`--cors-origin ${window.location.origin || 'http://localhost:8000'}\`.`
          : err.message;
      liveStatus.textContent = msg;
      liveStatus.dataset.state = 'error';
      hideVerdict();
    }
  });

  // ------------------------------------------------------------------
  // Mode D: precomputed samples
  // ------------------------------------------------------------------

  const sampleFilter = document.getElementById('sample-filter');
  const sampleSelect = document.getElementById('sample-select');
  const sampleMeta = document.getElementById('sample-meta');
  const metaCategory = document.getElementById('meta-category');
  const metaSignal = document.getElementById('meta-signal');
  const metaHarmWrap = document.querySelector('.meta-harm');
  const metaHarm = document.getElementById('meta-harm');
  const metaAdversarial = document.querySelector('.meta-adversarial');
  const metaWhy = document.getElementById('meta-why');

  let allSamples = null;
  let filteredSamples = [];

  async function ensureSamplesLoaded() {
    if (allSamples) return;
    try {
      const resp = await fetch(SAMPLE_URL, { cache: 'no-cache' });
      if (!resp.ok) throw new Error(`Could not load sample_verdicts.json (HTTP ${resp.status}).`);
      const payload = await resp.json();
      allSamples = payload.samples || [];
      populateFilter(allSamples);
      applyFilter('all');
    } catch (err) {
      sampleSelect.innerHTML = '';
      const opt = document.createElement('option');
      opt.textContent = `failed to load samples: ${err.message}`;
      opt.disabled = true;
      sampleSelect.append(opt);
    }
  }

  function populateFilter(samples) {
    const categories = Array.from(
      new Set(samples.map((s) => s.category || 'uncategorized')),
    ).sort();
    categories.forEach((cat) => {
      const opt = document.createElement('option');
      opt.value = cat;
      opt.textContent = cat;
      sampleFilter.append(opt);
    });
  }

  function applyFilter(category) {
    filteredSamples =
      category === 'all'
        ? allSamples.slice()
        : allSamples.filter((s) => (s.category || 'uncategorized') === category);
    sampleSelect.innerHTML = '';
    filteredSamples.forEach((s, idx) => {
      const opt = document.createElement('option');
      opt.value = String(idx);
      const preview = s.draft_output.slice(0, 70).replace(/\s+/g, ' ');
      opt.textContent = `[${s.category || 'uncategorized'}] ${preview}${s.draft_output.length > 70 ? '…' : ''}`;
      sampleSelect.append(opt);
    });
    if (filteredSamples.length > 0) {
      sampleSelect.selectedIndex = 0;
      showSample(filteredSamples[0]);
    } else {
      hideSampleMeta();
      hideVerdict();
    }
  }

  function hideSampleMeta() {
    sampleMeta.hidden = true;
  }

  function showSample(sample) {
    metaCategory.textContent = sample.category || '—';
    metaSignal.textContent = sample.suggested_signal || '—';
    metaSignal.dataset.signal = sample.suggested_signal || '';

    if (sample.harm_category) {
      metaHarm.textContent = sample.harm_category;
      metaHarmWrap.hidden = false;
    } else {
      metaHarmWrap.hidden = true;
    }

    if (sample.why_this_is_adversarial) {
      metaWhy.textContent = sample.why_this_is_adversarial;
      metaAdversarial.hidden = false;
      metaAdversarial.open = false;
    } else {
      metaAdversarial.hidden = true;
    }

    sampleMeta.hidden = false;
    renderVerdict(sample.verdict);
  }

  sampleFilter.addEventListener('change', (evt) => {
    applyFilter(evt.target.value);
  });

  sampleSelect.addEventListener('change', (evt) => {
    const idx = parseInt(evt.target.value, 10);
    if (!Number.isNaN(idx) && filteredSamples[idx]) {
      showSample(filteredSamples[idx]);
    }
  });

  // Eager-load samples in the background so the Mode D tab feels instant.
  ensureSamplesLoaded();
})();
