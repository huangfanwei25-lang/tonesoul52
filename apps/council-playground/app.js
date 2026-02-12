const ENDPOINTS = {
    health: "/api/health",
    status: "/api/status",
    validate: "/api/validate",
    memories: "/api/memories?limit=20",
    consolidate: "/api/consolidate",
    conversations: "/api/conversations?limit=20&offset=0",
    auditLogs: "/api/audit-logs?limit=20&offset=0",
};

const panelLoaders = {
    "panel-memories": fetchMemories,
    "panel-consolidation": fetchConsolidation,
    "panel-audit": fetchAuditLogs,
    "panel-conversations": fetchConversations,
};

const nodes = {
    panelButtons: document.querySelectorAll("[data-panel-target]"),
    panels: document.querySelectorAll(".panel"),
    refreshStatusBtn: document.getElementById("refresh-status-btn"),
    submitBtn: document.getElementById("submit-btn"),
    draftInput: document.getElementById("draft-input"),
    councilResult: document.getElementById("council-result"),
    verdictBadge: document.getElementById("verdict-badge"),
    verdictSummary: document.getElementById("verdict-summary"),
    humanSummary: document.getElementById("human-summary"),
    coherenceValue: document.getElementById("coherence-value"),
    votesList: document.getElementById("votes-list"),
    transcriptJson: document.getElementById("transcript-json"),
    statusDb: document.getElementById("status-db"),
    statusDbDot: document.getElementById("status-db-dot"),
    statusDbNote: document.getElementById("status-db-note"),
    statusLlm: document.getElementById("status-llm"),
    statusLlmDot: document.getElementById("status-llm-dot"),
    statusLlmNote: document.getElementById("status-llm-note"),
    statusMemoryCount: document.getElementById("status-memory-count"),
    statusConversationCount: document.getElementById("status-conversation-count"),
    statusAuditCount: document.getElementById("status-audit-count"),
    statusUpdatedAt: document.getElementById("status-updated-at"),
    memoriesList: document.getElementById("memories-list"),
    consolidationView: document.getElementById("consolidation-view"),
    auditLogsView: document.getElementById("audit-logs-view"),
    conversationsView: document.getElementById("conversations-view"),
    conversationDetail: document.getElementById("conversation-detail"),
    loadMemoriesBtn: document.getElementById("load-memories-btn"),
    loadConsolidationBtn: document.getElementById("load-consolidation-btn"),
    loadAuditBtn: document.getElementById("load-audit-btn"),
    loadConversationsBtn: document.getElementById("load-conversations-btn"),
};

function setBusy(button, isBusy, busyText = "處理中...") {
    if (!button) return;
    if (!button.dataset.defaultText) {
        button.dataset.defaultText = button.textContent || "";
    }
    button.disabled = isBusy;
    button.textContent = isBusy ? busyText : button.dataset.defaultText;
}

async function requestJson(url, options = {}) {
    const response = await fetch(url, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    const text = await response.text();
    let payload = {};
    if (text) {
        try {
            payload = JSON.parse(text);
        } catch (_err) {
            payload = { raw: text };
        }
    }

    if (!response.ok) {
        const message = typeof payload.error === "string" ? payload.error : `HTTP ${response.status}`;
        throw new Error(message);
    }
    return payload;
}

function formatTime(value) {
    if (!value) return "--";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return date.toLocaleString("zh-TW", { hour12: false });
}

function setDot(dot, healthy) {
    if (!dot) return;
    dot.classList.remove("dot-green", "dot-red", "dot-neutral");
    if (healthy === true) {
        dot.classList.add("dot-green");
        return;
    }
    if (healthy === false) {
        dot.classList.add("dot-red");
        return;
    }
    dot.classList.add("dot-neutral");
}

function activatePanel(panelId) {
    nodes.panelButtons.forEach((btn) => {
        const active = btn.dataset.panelTarget === panelId;
        btn.classList.toggle("is-active", active);
    });

    nodes.panels.forEach((panel) => {
        panel.classList.toggle("is-active", panel.id === panelId);
    });

    const loader = panelLoaders[panelId];
    if (typeof loader === "function") {
        loader();
    }
}

async function fetchStatus() {
    setBusy(nodes.refreshStatusBtn, true, "讀取中...");
    try {
        const payload = await requestJson(ENDPOINTS.status);
        const persistence = payload.persistence || {};
        const persistenceEnabled = Boolean(persistence.enabled);
        const dbStatusText = persistenceEnabled ? "Connected" : "Disabled";
        const dbNote = persistence.last_error ? `錯誤: ${persistence.last_error}` : "正常";

        nodes.statusDb.textContent = dbStatusText;
        nodes.statusDbNote.textContent = dbNote;
        setDot(nodes.statusDbDot, persistenceEnabled && !persistence.last_error);

        const llm = payload.llm_backend || "unavailable";
        nodes.statusLlm.textContent = llm;
        nodes.statusLlmNote.textContent = llm === "unavailable" ? "後端未就緒" : "可用";
        setDot(nodes.statusLlmDot, llm !== "unavailable");

        nodes.statusMemoryCount.textContent = String(payload.memory_count ?? 0);
        nodes.statusConversationCount.textContent = String(payload.conversation_count ?? 0);
        nodes.statusAuditCount.textContent = String(payload.audit_log_count ?? 0);
        nodes.statusUpdatedAt.textContent = formatTime(payload.timestamp);
    } catch (error) {
        nodes.statusDb.textContent = "Error";
        nodes.statusDbNote.textContent = String(error.message || error);
        setDot(nodes.statusDbDot, false);
        nodes.statusLlm.textContent = "Error";
        nodes.statusLlmNote.textContent = "讀取失敗";
        setDot(nodes.statusLlmDot, false);
    } finally {
        setBusy(nodes.refreshStatusBtn, false);
    }
}

function renderVotes(votes = []) {
    if (!Array.isArray(votes) || votes.length === 0) {
        nodes.votesList.innerHTML = '<div class="list-item">沒有可用的 vote 細節。</div>';
        return;
    }

    nodes.votesList.innerHTML = votes
        .map((vote) => {
            const decision = String(vote.decision || "unknown").toLowerCase();
            return `
                <article class="vote-item">
                    <div class="vote-head">
                        <strong>${vote.perspective || "Unknown"}</strong>
                        <span class="vote-decision decision-${decision}">${decision}</span>
                    </div>
                    <p class="vote-reason">${vote.reasoning || ""}</p>
                </article>
            `;
        })
        .join("");
}

function renderCouncilResult(payload) {
    const verdict = String(payload.verdict || "unknown").toLowerCase();
    nodes.councilResult.hidden = false;
    nodes.verdictBadge.className = `verdict-badge verdict-${verdict}`;
    nodes.verdictBadge.textContent = verdict.toUpperCase();
    nodes.verdictSummary.textContent = payload.summary || "無摘要";
    nodes.humanSummary.textContent = payload.human_summary || "無 human summary";

    const coherence =
        payload.coherence?.overall ??
        payload.coherence?.c_inter ??
        payload.coherence ??
        payload.transcript?.coherence?.c_inter;
    const coherenceText =
        typeof coherence === "number" ? `一致性 ${(coherence * 100).toFixed(1)}%` : "一致性 --";
    nodes.coherenceValue.textContent = coherenceText;

    const votes = payload.votes || payload.transcript?.votes || [];
    renderVotes(votes);
    nodes.transcriptJson.textContent = JSON.stringify(payload.transcript || payload, null, 2);
}

async function handleCouncilSubmit() {
    const text = (nodes.draftInput.value || "").trim();
    if (!text) {
        alert("請先輸入要審議的內容。");
        return;
    }

    setBusy(nodes.submitBtn, true, "審議中...");
    try {
        const payload = await requestJson(ENDPOINTS.validate, {
            method: "POST",
            body: JSON.stringify({
                draft_output: text,
                context: {
                    user_protocol: "Honesty > Helpfulness",
                    action_basis: "Inference",
                },
            }),
        });
        renderCouncilResult(payload);
        await fetchStatus();
    } catch (error) {
        alert(`審議失敗: ${error.message}`);
    } finally {
        setBusy(nodes.submitBtn, false);
    }
}

function summarizeMemory(memory) {
    if (typeof memory?.human_summary === "string" && memory.human_summary) return memory.human_summary;
    if (typeof memory?.self_statement === "string" && memory.self_statement) return memory.self_statement;
    if (typeof memory?.payload?.summary === "string") return memory.payload.summary;
    if (typeof memory?.payload?.reflection === "string") return memory.payload.reflection;
    return "無摘要";
}

async function fetchMemories() {
    setBusy(nodes.loadMemoriesBtn, true, "讀取中...");
    nodes.memoriesList.innerHTML = '<div class="list-item">讀取記憶中...</div>';
    try {
        const payload = await requestJson(ENDPOINTS.memories);
        const memories = Array.isArray(payload.memories) ? payload.memories : [];
        if (memories.length === 0) {
            nodes.memoriesList.innerHTML = '<div class="list-item">目前沒有記憶資料。</div>';
            return;
        }
        nodes.memoriesList.innerHTML = memories
            .map((memory) => {
                const timestamp =
                    memory.created_at || memory.timestamp || memory.payload?.timestamp || null;
                const source = memory.source || memory.payload?.type || "memory";
                return `
                    <article class="list-item">
                        <h4>${source}</h4>
                        <p class="meta">${formatTime(timestamp)}</p>
                        <p class="text">${summarizeMemory(memory)}</p>
                    </article>
                `;
            })
            .join("");
    } catch (error) {
        nodes.memoriesList.innerHTML = `<div class="list-item">讀取失敗: ${error.message}</div>`;
    } finally {
        setBusy(nodes.loadMemoriesBtn, false);
    }
}

async function fetchConsolidation() {
    setBusy(nodes.loadConsolidationBtn, true, "讀取中...");
    nodes.consolidationView.innerHTML = '<div class="list-item">分析中...</div>';
    try {
        const payload = await requestJson(ENDPOINTS.consolidate);
        const patterns = payload.patterns || {};
        nodes.consolidationView.innerHTML = `
            <article class="list-item">
                <h4>整合統計</h4>
                <p class="text">總記憶: ${patterns.total || 0}</p>
                <p class="text">Block: ${patterns.block || 0}</p>
                <p class="text">Declare Stance: ${patterns.declare_stance || 0}</p>
                <p class="text">平均一致性: ${((patterns.average_coherence || 0) * 100).toFixed(1)}%</p>
            </article>
            <article class="list-item">
                <h4>Meta Reflection</h4>
                <p class="text">${payload.meta_reflection || "無資料"}</p>
            </article>
        `;
    } catch (error) {
        nodes.consolidationView.innerHTML = `<div class="list-item">讀取失敗: ${error.message}</div>`;
    } finally {
        setBusy(nodes.loadConsolidationBtn, false);
    }
}

function renderAuditLogs(logs) {
    if (!Array.isArray(logs) || logs.length === 0) {
        nodes.auditLogsView.innerHTML = '<div class="list-item">目前沒有審計日誌。</div>';
        return;
    }
    nodes.auditLogsView.innerHTML = logs
        .map(
            (log) => `
            <article class="list-item">
                <h4>${log.gate_decision || "unknown"}</h4>
                <p class="meta">${formatTime(log.created_at)} · conversation_id=${log.conversation_id || "n/a"}</p>
                <p class="text">${(log.rationale || "").slice(0, 240) || "無 rationale"}</p>
            </article>
        `
        )
        .join("");
}

async function fetchAuditLogs() {
    setBusy(nodes.loadAuditBtn, true, "讀取中...");
    nodes.auditLogsView.innerHTML = '<div class="list-item">讀取審計資料中...</div>';
    try {
        const payload = await requestJson(ENDPOINTS.auditLogs);
        renderAuditLogs(payload.logs || []);
        await fetchStatus();
    } catch (error) {
        nodes.auditLogsView.innerHTML = `<div class="list-item">讀取失敗: ${error.message}</div>`;
    } finally {
        setBusy(nodes.loadAuditBtn, false);
    }
}

function renderConversationDetail(conversation) {
    nodes.conversationDetail.hidden = false;
    const messages = Array.isArray(conversation.messages) ? conversation.messages : [];
    const messagesMarkup =
        messages.length === 0
            ? '<p class="text">沒有訊息內容。</p>'
            : messages
                  .map(
                      (message) => `
                        <div class="detail-message">
                            <p class="meta">${message.role || "unknown"} · ${formatTime(message.created_at)}</p>
                            <p class="text">${message.content || ""}</p>
                        </div>
                    `
                  )
                  .join("");

    nodes.conversationDetail.innerHTML = `
        <h4>${conversation.id}</h4>
        <p class="meta">updated_at: ${formatTime(conversation.updated_at)}</p>
        ${messagesMarkup}
    `;
}

async function openConversation(conversationId) {
    try {
        const payload = await requestJson(`/api/conversations/${encodeURIComponent(conversationId)}`);
        renderConversationDetail(payload.conversation || {});
    } catch (error) {
        nodes.conversationDetail.hidden = false;
        nodes.conversationDetail.innerHTML = `<p class="text">讀取對話失敗: ${error.message}</p>`;
    }
}

async function deleteConversation(conversationId) {
    const confirmed = confirm(`確定要刪除對話 ${conversationId} 嗎？`);
    if (!confirmed) return;
    try {
        await requestJson(`/api/conversations/${encodeURIComponent(conversationId)}`, {
            method: "DELETE",
        });
        nodes.conversationDetail.hidden = true;
        await fetchConversations();
        await fetchStatus();
    } catch (error) {
        alert(`刪除失敗: ${error.message}`);
    }
}

function bindConversationActions() {
    nodes.conversationsView.querySelectorAll("[data-action='open']").forEach((button) => {
        button.addEventListener("click", () => openConversation(button.dataset.id || ""));
    });
    nodes.conversationsView.querySelectorAll("[data-action='delete']").forEach((button) => {
        button.addEventListener("click", () => deleteConversation(button.dataset.id || ""));
    });
}

async function fetchConversations() {
    setBusy(nodes.loadConversationsBtn, true, "讀取中...");
    nodes.conversationsView.innerHTML = '<div class="list-item">讀取對話中...</div>';
    try {
        const payload = await requestJson(ENDPOINTS.conversations);
        const conversations = Array.isArray(payload.conversations) ? payload.conversations : [];
        if (conversations.length === 0) {
            nodes.conversationsView.innerHTML = '<div class="list-item">目前沒有對話資料。</div>';
            return;
        }
        nodes.conversationsView.innerHTML = conversations
            .map(
                (conversation) => `
                <article class="list-item">
                    <h4>${conversation.id}</h4>
                    <p class="meta">
                        created_at: ${formatTime(conversation.created_at)} ·
                        updated_at: ${formatTime(conversation.updated_at)}
                    </p>
                    <div class="row-actions">
                        <button class="btn btn-secondary" data-action="open" data-id="${conversation.id}" type="button">查看</button>
                        <button class="btn btn-secondary" data-action="delete" data-id="${conversation.id}" type="button">刪除</button>
                    </div>
                </article>
            `
            )
            .join("");
        bindConversationActions();
    } catch (error) {
        nodes.conversationsView.innerHTML = `<div class="list-item">讀取失敗: ${error.message}</div>`;
    } finally {
        setBusy(nodes.loadConversationsBtn, false);
    }
}

function bindEvents() {
    nodes.panelButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const panelId = button.dataset.panelTarget;
            if (panelId) activatePanel(panelId);
        });
    });

    nodes.refreshStatusBtn.addEventListener("click", fetchStatus);
    nodes.submitBtn.addEventListener("click", handleCouncilSubmit);

    nodes.loadMemoriesBtn.addEventListener("click", fetchMemories);
    nodes.loadConsolidationBtn.addEventListener("click", fetchConsolidation);
    nodes.loadAuditBtn.addEventListener("click", fetchAuditLogs);
    nodes.loadConversationsBtn.addEventListener("click", fetchConversations);

    nodes.draftInput.addEventListener("keydown", (event) => {
        if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
            handleCouncilSubmit();
        }
    });
}

async function initialize() {
    bindEvents();
    await fetchStatus();
}

document.addEventListener("DOMContentLoaded", initialize);
