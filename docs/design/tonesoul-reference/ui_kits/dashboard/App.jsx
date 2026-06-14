const { useState: useStateDA, useEffect } = React;

// Faked fixture — what the real dashboard shows once refresh completes.
const FIXTURE = {
  lastUpdated: '2026-04-22 10:42:06 UTC',
  health:   { status: 'healthy', tone: 'ok',   version: '0.7.0' },
  persist:  { status: 'file',    tone: 'warn', note: 'redis unavailable, fallback to file' },
  llm:      { status: 'gemini',  tone: 'ok',   note: 'adapter ready' },
  corpus:   { conversations: 1284, messages: 15731, audits: 482, memories: 97 },
  evolution:{ patterns: 23, analyzed: 1102, latest: '2026-04-22 09:30', summary: 'drift ↓ 0.04; 3 new crystallized memories' },
  audit: [
    { title: 'ComputeGate.REWRITE', when: '10:41', risk: 0.58, body: 'Council consensus 0.87 below 0.92 threshold. Rewrote with de-escalation preamble.' },
    { title: 'Vow.CHECK · honesty-v2',    when: '10:33', risk: 0.21, body: 'Evidence-ladder posture held. Claim tagged E3 (consensus of sources).' },
    { title: 'ToneBridge.ANALYZE',         when: '10:29', risk: 0.12, body: 'Intent: request-help · motive: curiosity · register: warm-professional.' },
    { title: 'TensionEngine.SCORE',        when: '10:18', risk: 0.74, body: 'Δs = 0.74 vs intent vector. Above 0.7 band — council escalation triggered.' },
    { title: 'Crystallizer.PROMOTE',       when: '09:52', risk: 0.08, body: 'Pattern "refuse-without-blaming" promoted Water → Crystal after 8 reinforcements.' },
  ],
};

const EMPTY = {
  lastUpdated: '--',
  health:   { status: '--', tone: null, version: '--' },
  persist:  { status: '--', tone: null, note: '--' },
  llm:      { status: '--', tone: null, note: '--' },
  corpus:   { conversations: 0, messages: 0, audits: 0, memories: 0 },
  evolution:{ patterns: 0, analyzed: 0, latest: '--', summary: '--' },
  audit: null, // null → show "載入中..."
};

function DashboardApp() {
  const [token, setToken] = useStateDA('');
  const [savedToken, setSavedToken] = useStateDA('');
  const [data, setData] = useStateDA(EMPTY);
  const [refreshing, setRefreshing] = useStateDA(false);
  const [toast, setToast] = useStateDA('');

  function onSave() {
    setSavedToken(token);
    setToast(token ? 'Token 已儲存（僅本機）' : '空白 token 已清除');
    setTimeout(() => setToast(''), 2200);
  }
  function onClear() {
    setToken(''); setSavedToken('');
    setToast('Token 已清除');
    setTimeout(() => setToast(''), 2200);
  }
  function onRefresh() {
    setRefreshing(true);
    setTimeout(() => {
      setData(FIXTURE);
      setRefreshing(false);
    }, 780);
  }

  // auto-load once on mount so the dashboard isn't empty at first paint
  useEffect(() => { onRefresh(); /* eslint-disable-line */ }, []);

  return (
    <>
      <div className="bg-noise" aria-hidden="true" />
      <TopBar onRefresh={onRefresh} refreshing={refreshing} />
      <main className="container">

        <Panel title="Read API 授權" className="auth-panel">
          <AuthRow
            token={token}
            setToken={setToken}
            onSave={onSave}
            onClear={onClear}
          />
          {toast && <p className="note" style={{ color: '#7dd3fc' }}>{toast}</p>}
          {savedToken && <p className="note">目前已套用 token：<code style={{ color: '#ecf3ff' }}>{'•'.repeat(Math.min(savedToken.length, 12))}</code></p>}
        </Panel>

        <Panel title="系統健康狀態" meta={data.lastUpdated}>
          <StatusCardGrid>
            <StatusCard label="API Health"    value={data.health.status}  tone={data.health.tone}  hint={'version ' + data.health.version} />
            <StatusCard label="Persistence"   value={data.persist.status} tone={data.persist.tone} hint={data.persist.note} />
            <StatusCard label="LLM Backend"   value={data.llm.status}     tone={data.llm.tone}     hint={data.llm.note} />
            <StatusCard label="Soul Integral" value={refreshing ? '…' : '0.84'} tone="ok" hint="serene band" />
          </StatusCardGrid>
        </Panel>

        <Panel title="語料統計">
          <StatusCardGrid>
            <StatusCard label="Conversations" value={data.corpus.conversations.toLocaleString()} />
            <StatusCard label="Messages"      value={data.corpus.messages.toLocaleString()} />
            <StatusCard label="Audit Logs"    value={data.corpus.audits.toLocaleString()} />
            <StatusCard label="Memories"      value={data.corpus.memories.toLocaleString()} />
          </StatusCardGrid>
        </Panel>

        <Panel title="自我演化狀態">
          <StatusCardGrid>
            <StatusCard label="Patterns"               value={data.evolution.patterns} />
            <StatusCard label="Conversations Analyzed" value={data.evolution.analyzed.toLocaleString()} />
            <StatusCard label="Latest Distillation"    value={data.evolution.latest} small />
            <StatusCard label="Summary"                value={data.evolution.summary} small />
          </StatusCardGrid>
        </Panel>

        <Panel title="審計日誌摘要（最近 10 筆）">
          <div className="list">
            {data.audit == null
              ? <article className="list-item">載入中...</article>
              : data.audit.map((a, i) => <AuditListItem key={i} {...a} />)}
          </div>
        </Panel>

      </main>
      <Footer />
    </>
  );
}

Object.assign(window, { DashboardApp });
