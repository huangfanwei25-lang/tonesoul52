// Dashboard kit — obsidian components
const { useState: useStateD } = React;

function TopBar({ onRefresh, refreshing }) {
  return (
    <header className="topbar">
      <div className="brand">
        <span className="brand-mark">TS</span>
        <div>
          <p className="brand-title">ToneSoul 後端觀測儀表板</p>
          <p className="brand-subtitle">Backend is for AI services, not user chat UI</p>
        </div>
      </div>
      <div className="topbar-actions">
        <button className="btn btn-primary" onClick={onRefresh} disabled={refreshing}>
          {refreshing ? '更新中…' : '重新整理'}
        </button>
      </div>
    </header>
  );
}

function Panel({ title, meta, children, className }) {
  return (
    <section className={'panel ' + (className || '')}>
      <div className="panel-header">
        <h2>{title}</h2>
        {meta != null && <p className="meta">{meta}</p>}
      </div>
      {children}
    </section>
  );
}

function StatusCard({ label, value, hint, tone, small }) {
  const toneClass = tone ? ' is-' + tone : '';
  return (
    <article className="status-card">
      <p className="label">{label}</p>
      <p className={'value' + (small ? ' small' : '') + toneClass}>{value}</p>
      {hint != null && <p className="hint">{hint}</p>}
    </article>
  );
}

function StatusCardGrid({ children }) {
  return <div className="card-grid">{children}</div>;
}

function AuthRow({ token, setToken, onSave, onClear }) {
  return (
    <>
      <div className="auth-row">
        <input
          className="input"
          type="password"
          autoComplete="off"
          placeholder="如果後端設定 TONESOUL_READ_API_TOKEN，請輸入 token"
          value={token}
          onChange={e => setToken(e.target.value)}
        />
        <button className="btn btn-secondary" onClick={onSave}>儲存</button>
        <button className="btn btn-secondary" onClick={onClear}>清除</button>
      </div>
      <p className="note">未設定 token 也可使用；若讀取 API 回傳 401，再輸入 token。</p>
    </>
  );
}

function AuditListItem({ title, when, risk, body }) {
  return (
    <article className="list-item">
      <div className="list-item-head">
        <p className="list-item-title">{title}</p>
        <p className="list-item-meta">{when} · risk {risk}</p>
      </div>
      <p className="list-item-body">{body}</p>
    </article>
  );
}

function Footer() {
  return (
    <footer className="footer">
      <a href="#" onClick={e => e.preventDefault()}>github.com/Fan1234-1/tonesoul52</a>
      <span>Playground v0.7.0</span>
    </footer>
  );
}

Object.assign(window, { TopBar, Panel, StatusCard, StatusCardGrid, AuthRow, AuditListItem, Footer });
