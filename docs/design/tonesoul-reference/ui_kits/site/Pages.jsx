const { useState: useStateP } = React;

const FEATURES = [
  { title: 'Tension Engine', body: 'Every response is scored for semantic deviation before it ships. Drift is measured, not guessed.' },
  { title: 'Council Deliberation', body: 'Multiple perspectives (Guardian, Analyst, Critic, Advocate) debate before final output. Dissent survives.' },
  { title: 'Self-Governance', body: 'Unsafe or incoherent output is blocked or rewritten — with full audit trails. Not just flagged.' },
  { title: 'Memory with Decay', body: 'Important patterns crystallize. Noise fades. Exponential decay + phase transitions (Ice → Water → Steam → Crystal).' },
  { title: 'Reflex Arc', body: 'Governance state directly affects behavior. Soul bands (serene → critical) tighten or relax output gates in real-time.' },
  { title: 'Vow System', body: 'AI makes commitments (vows) and is held to them. Violations are blocked, not just logged. Conviction decays are detected.' },
];

const AXIOMS = [
  { n: 1, name: 'Continuity', fol: '∀e ∈ Events : in_time_island(e) ∧ traceable(e)', body: 'Every event must belong to a traceable chain. Nothing happens outside of history — orphan events are impossible.' },
  { n: 2, name: 'Responsibility Threshold', fol: 'Risk(e) > 0.4 → ∃log : immutable(log, e)', body: 'High-risk actions require an immutable audit log. Risk cannot be discarded; it must be inherited.' },
  { n: 3, name: 'Governance Gate', fol: 'Major(d) → consensus(d) ≥ 0.92', body: 'Decisions above a materiality threshold require near-unanimous council consensus before they ship.' },
  { n: 4, name: 'Non-Zero Tension', fol: 'lim_{t→∞} T(t) > 0', body: 'A system with zero tension is dead. Life requires a minimal gradient of tension to drive evolution — the goal is equilibrium, not nullity.' },
  { n: 5, name: 'Mirror Recursion', fol: 'reflect(reflect(s)) ⊨ accuracy↑', body: 'Self-reflection must increase accuracy, not just repeat. Each mirror pass is expected to reduce error, or it is wasted.' },
  { n: 6, name: 'User Sovereignty', fol: '∀a : harms(a, user) → block(a)', body: 'No action may harm the user. Priority P0, overriding all other objectives. The system is in service of a person, not the reverse.' },
  { n: 7, name: 'Semantic Field Conservation', fol: 'amplify(signal) ≤ 1.0', body: 'The system is a damper, not an amplifier. It may attenuate noise but may not amplify bias.' },
];

function HomePage({ onGo }) {
  return (
    <>
      <Hero onGo={onGo} />
      <main>
        <h2>The Problem</h2>
        <p>Most AI systems are built to agree. Disagreement feels broken. But agreement without friction is how bias spreads, errors persist, and truth gets smoothed over.</p>
        <p>ToneSoul is built around a single uncomfortable design principle:</p>
        <Blockquote lead="A system with zero tension is dead." cite="Axiom 4: Non-Zero Tension Principle" />
        <p>The goal is not a frictionless assistant. The goal is an assistant that has <strong>character</strong> — meaning: under pressure, its choices remain traceable and consistent.</p>

        <h2>What ToneSoul Does</h2>
        <div className="grid">
          {FEATURES.map(f => <FeatureCard key={f.title} {...f} />)}
        </div>

        <h2>How It Differs</h2>
        <ComparisonTable />

        <h2>Architecture Overview</h2>
        <CodeBlock>{`User Input
    ↓
[ToneBridge] Analyze tone, motive, context
    ↓
[TensionEngine] Compute semantic deviation
    ↓
[Reflex Arc] Soul band → gate modifier → enforcement
    ↓
[Council] Guardian / Analyst / Critic / Advocate deliberate
    ↓
[ComputeGate] Approve / Block / Rewrite
    ↓
[Crystallizer] Remember what matters, forget the rest
    ↓
Response (with audit trail)`}</CodeBlock>

        <h2>Quick Start</h2>
        <CodeBlock>pip install tonesoul52</CodeBlock>
        <p><button className="cta cta-secondary" onClick={() => onGo('start')}>Full getting started guide →</button></p>
      </main>
    </>
  );
}

function ConceptsPage() {
  return (
    <main>
      <p className="breadcrumb">Home › Philosophy</p>
      <h1 style={{ fontSize: '2rem' }}>The Seven Axioms</h1>
      <p>ToneSoul is governed by seven immutable laws. They are not configurable; they bound the whole system.</p>
      {AXIOMS.map(a => <AxiomCard key={a.n} {...a} />)}
    </main>
  );
}

function StartPage() {
  const [step, setStep] = useStateP(1);
  return (
    <main>
      <p className="breadcrumb">Home › Get Started</p>
      <h1 style={{ fontSize: '2rem' }}>Getting Started</h1>
      <p>Install ToneSoul, load a governance posture, and run the tension dashboard.</p>

      <Step n={1} title="Install">
        <CodeBlock>pip install tonesoul52</CodeBlock>
        <p>Requires Python 3.10 or newer. Apache 2.0 license.</p>
      </Step>

      <Step n={2} title="Load a governance posture">
        <CodeBlock>{`from tonesoul.runtime_adapter import load, commit

posture = load()
print(f"Soul Integral: {posture.soul_integral}")
print(f"Active Vows: {len(posture.active_vows)}")`}</CodeBlock>
      </Step>

      <Step n={3} title="Run the dashboard">
        <CodeBlock>python scripts/tension_dashboard.py --work-category research</CodeBlock>
        <Note><strong>Note.</strong> On first run, persistence falls back to file storage when Redis is unavailable. The dashboard will flag this under Persistence.</Note>
      </Step>

      <div style={{ marginTop: '2rem' }}>
        <button className="cta cta-secondary" onClick={() => setStep(s => Math.max(1, s - 1))}>← Previous</button>
        <button className="cta cta-primary" onClick={() => setStep(s => Math.min(3, s + 1))}>Next →</button>
        <span style={{ marginLeft: '1rem', color: 'var(--text-muted)', fontSize: '.88rem' }}>Step {step} / 3</span>
      </div>
    </main>
  );
}

function StoryPage() {
  return (
    <main>
      <p className="breadcrumb">Home › Origin</p>
      <h1 style={{ fontSize: '2rem' }}>Origin</h1>
      <Blockquote
        lead="ToneSoul began with one unanswered question: what would it mean for a language model to be accountable to itself?"
        cite="Fan-Wei Huang · 黃梵威"
      />
      <p>This framework is the continuing answer: not a personality for the model, but a ledger of its choices. A way for the system to own what it has said, and to know — precisely — when it is drifting from who it has promised to be.</p>
      <p>The name is deliberate. <em>Tone</em> is the felt quality of speech; <em>soul</em> is the throughline that makes a speaker recognizable across time. Together: a system that can be trusted because its choices are legible, not because its compliance is perfect.</p>
    </main>
  );
}

function SiteApp() {
  const [page, setPage] = useStateP('home');
  return (
    <div className="page">
      <SiteNav current={page} onGo={setPage} />
      {page === 'home' && <HomePage onGo={setPage} />}
      {page === 'concepts' && <ConceptsPage />}
      {page === 'start' && <StartPage />}
      {page === 'story' && <StoryPage />}
      <SiteFooter />
    </div>
  );
}

Object.assign(window, { HomePage, ConceptsPage, StartPage, StoryPage, SiteApp });
