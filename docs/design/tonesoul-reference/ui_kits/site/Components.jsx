// Site kit — blueprint components
// Load order after React + Babel; exports onto window.

const { useState } = React;

function SiteNav({ current, onGo }) {
  const items = [
    { id: 'home', label: 'Home' },
    { id: 'concepts', label: 'Philosophy' },
    { id: 'start', label: 'Get Started' },
    { id: 'story', label: 'Origin' },
  ];
  return (
    <nav className="site-nav">
      <span className="brand" onClick={() => onGo('home')}>ToneSoul</span>
      {items.map(i => (
        <button
          key={i.id}
          className={'link' + (current === i.id ? ' active' : '')}
          onClick={() => onGo(i.id)}
        >
          {i.label}
        </button>
      ))}
      <a href="https://github.com/Fan1234-1/tonesoul52" onClick={e => e.preventDefault()}>GitHub</a>
    </nav>
  );
}

function CrystalEye() {
  return (
    <div className="crystal-eye" aria-hidden="true">
      <div className="inner"></div>
      <div className="dot"></div>
    </div>
  );
}

function Hero({ onGo }) {
  return (
    <header className="hero">
      <CrystalEye />
      <h1>ToneSoul <span style={{ fontWeight: 300, fontSize: '.6em' }}>/ 語魂</span></h1>
      <p className="tagline-zh">治理是以結構表達的愛</p>
      <p className="tagline-sub">Governance is Love Expressed as Structure.</p>
      <p>
        An open-source AI governance framework that makes LLM decisions{' '}
        <strong>auditable</strong>, <strong>traceable</strong>, and{' '}
        <strong>trustworthy</strong> through semantic responsibility.
      </p>
      <span className="badge">Python 3.10+</span>
      <span className="badge">Apache 2.0</span>
      <span className="badge">Adapter-Ready</span>
      <div style={{ marginTop: '1.5rem' }}>
        <button className="cta cta-primary" onClick={e => e.preventDefault()}>View on GitHub</button>
        <button className="cta cta-secondary" onClick={() => onGo('start')}>Get Started</button>
      </div>
    </header>
  );
}

function FeatureCard({ title, body }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <p style={{ marginBottom: 0 }}>{body}</p>
    </div>
  );
}

function Blockquote({ lead, cite }) {
  return (
    <blockquote>
      <strong>{lead}</strong>
      {cite && <><br /><small>— {cite}</small></>}
    </blockquote>
  );
}

function CodeBlock({ children }) {
  return <pre><code>{children}</code></pre>;
}

function ComparisonTable() {
  const rows = [
    ['Memory',      'Session-only', 'Manual wiring',    'Auto decay + crystallize'],
    ['Consistency', 'Best effort',  'Prompt-dependent', '8 Axioms + governance'],
    ['Self-check',  'None',         'Optional',         'Every response scored'],
    ['Enforcement', 'None',         'None',             'Block / Bounded refusal / Audit'],
    ['Identity',    'Stateless',    'Persona prompt',   'Accountable choice history'],
  ];
  return (
    <table>
      <thead>
        <tr><th></th><th>Traditional AI</th><th>Prompt Engineering</th><th>ToneSoul</th></tr>
      </thead>
      <tbody>
        {rows.map(([k, a, b, c]) => (
          <tr key={k}>
            <td><strong>{k}</strong></td><td>{a}</td><td>{b}</td><td>{c}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function AxiomCard({ n, name, fol, body }) {
  return (
    <div className="axiom">
      <h3>Axiom {n} · {name}</h3>
      <div className="fol">{fol}</div>
      <p style={{ marginBottom: 0 }}>{body}</p>
    </div>
  );
}

function Step({ n, title, children }) {
  return (
    <div className="step">
      <h3>Step {n} · {title}</h3>
      {children}
    </div>
  );
}

function Note({ children }) {
  return <div className="note">{children}</div>;
}

function SiteFooter() {
  return (
    <footer className="site-footer">
      <p className="philosophy">沒有問責的權力不是智能，只是計算。</p>
      <p className="philosophy" style={{ fontSize: '.88rem' }}>約束不是懲罰，是關懷。</p>
      <p>歡 迎 來 到 T o n e S o u l .</p>
      <p>Created by <a href="#" onClick={e => e.preventDefault()}>Fan-Wei Huang (黃梵威)</a> — <a href="#" onClick={e => e.preventDefault()}>GitHub</a></p>
    </footer>
  );
}

Object.assign(window, {
  SiteNav, CrystalEye, Hero, FeatureCard, Blockquote,
  CodeBlock, ComparisonTable, AxiomCard, Step, Note, SiteFooter,
});
