const ENDPOINTS = {
    health: "/api/health",
    status: "/api/status",
    auditLogs: "/api/audit-logs?limit=10&offset=0",
    evolutionSummary: "/api/evolution/summary",
};

const READ_TOKEN_STORAGE_KEY = "tonesoul_playground_read_token";

const state = {
    readToken: "",
};

const nodes = {
    refreshAllBtn: document.getElementById("refresh-all-btn"),
    readTokenInput: document.getElementById("read-token-input"),
    saveTokenBtn: document.getElementById("save-token-btn"),
    clearTokenBtn: document.getElementById("clear-token-btn"),
    authNote: document.getElementById("auth-note"),
    lastUpdated: document.getElementById("last-updated"),
    healthStatus: document.getElementById("health-status"),
    healthVersion: document.getElementById("health-version"),
    persistenceStatus: document.getElementById("persistence-status"),
    persistenceNote: document.getElementById("persistence-note"),
    llmStatus: document.getElementById("llm-status"),
    llmNote: document.getElementById("llm-note"),
    statConversations: document.getElementById("stat-conversations"),
    statMessages: document.getElementById("stat-messages"),
    statAudits: document.getElementById("stat-audits"),
    statMemories: document.getElementById("stat-memories"),
    evolutionPatterns: document.getElementById("evolution-patterns"),
    evolutionAnalyzed: document.getElementById("evolution-analyzed"),
    evolutionLatest: document.getElementById("evolution-latest"),
    evolutionSummary: document.getElementById("evolution-summary"),
    auditList: document.getElementById("audit-list"),
};

function setBusy(button, isBusy, busyText = "Loading...") {
    if (!button) return;
    if (!button.dataset.defaultText) {
        button.dataset.defaultText = button.textContent || "";
    }
    button.disabled = isBusy;
    button.textContent = isBusy ? busyText : button.dataset.defaultText;
}

function formatTime(value) {
    if (!value) return "--";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return date.toLocaleString("zh-TW", { hour12: false });
}

function setStatusClass(node, status) {
    if (!node) return;
    node.classList.remove("is-ok", "is-warn", "is-error");
    if (status === "ok") node.classList.add("is-ok");
    if (status === "warn") node.classList.add("is-warn");
    if (status === "error") node.classList.add("is-error");
}

function getStoredReadToken() {
    try {
        return localStorage.getItem(READ_TOKEN_STORAGE_KEY) || "";
    } catch (_err) {
        return "";
    }
}

function setStoredReadToken(value) {
    try {
        if (value) {
            localStorage.setItem(READ_TOKEN_STORAGE_KEY, value);
        } else {
            localStorage.removeItem(READ_TOKEN_STORAGE_KEY);
        }
    } catch (_err) {
        // Ignore localStorage write failures in restricted contexts.
    }
}

function renderAuthNote() {
    if (!nodes.authNote) return;
    nodes.authNote.textContent = state.readToken
        ? "Read token 已儲存，讀取 API 會自動附帶 Authorization。"
        : "未設定 token 也可使用；若讀取 API 回傳 401，再輸入 token。";
}

function initializeToken() {
    const queryToken = new URLSearchParams(window.location.search).get("read_token");
    if (typeof queryToken === "string" && queryToken.trim()) {
        state.readToken = queryToken.trim();
        setStoredReadToken(state.readToken);
    } else {
        state.readToken = getStoredReadToken().trim();
    }
    if (nodes.readTokenInput) {
        nodes.readTokenInput.value = state.readToken;
    }
    renderAuthNote();
}

async function requestJson(url, options = {}) {
    const headers = { ...(options.headers || {}) };
    if (state.readToken && !headers.Authorization) {
        headers.Authorization = `Bearer ${state.readToken}`;
    }

    const response = await fetch(url, { ...options, headers });
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

async function fetchHealthAndStatus() {
    const [healthPayload, statusPayload] = await Promise.all([
        requestJson(ENDPOINTS.health),
        requestJson(ENDPOINTS.status),
    ]);

    nodes.healthStatus.textContent = String(healthPayload.status || "unknown");
    nodes.healthVersion.textContent = `version ${healthPayload.version || "--"}`;
    setStatusClass(nodes.healthStatus, healthPayload.status === "ok" ? "ok" : "error");

    const persistence = statusPayload.persistence || {};
    const persistenceEnabled = Boolean(persistence.enabled);
    nodes.persistenceStatus.textContent = persistenceEnabled ? "enabled" : "disabled";
    nodes.persistenceNote.textContent = persistence.last_error || "no error";
    setStatusClass(
        nodes.persistenceStatus,
        persistenceEnabled ? (persistence.last_error ? "warn" : "ok") : "warn"
    );

    const llmBackend = statusPayload.llm_backend || "unavailable";
    nodes.llmStatus.textContent = String(llmBackend);
    nodes.llmNote.textContent = statusPayload.llm_error || `mode=${statusPayload.llm_mode || "auto"}`;
    setStatusClass(nodes.llmStatus, llmBackend === "unavailable" ? "warn" : "ok");

    nodes.statConversations.textContent = String(statusPayload.conversation_count || 0);
    nodes.statMessages.textContent = String(statusPayload.message_count || 0);
    nodes.statAudits.textContent = String(statusPayload.audit_log_count || 0);
    nodes.statMemories.textContent = String(statusPayload.memory_count || 0);
}

function renderAuditLogs(logs) {
    if (!Array.isArray(logs) || logs.length === 0) {
        nodes.auditList.innerHTML = '<article class="list-item">尚無審計日誌。</article>';
        return;
    }
    nodes.auditList.innerHTML = logs
        .map((log) => {
            const createdAt = formatTime(log.created_at);
            const title = String(log.gate_decision || "unknown");
            const conversationId = log.conversation_id || "n/a";
            const rationale = String(log.rationale || "").slice(0, 240) || "no rationale";
            return `
                <article class="list-item">
                    <div class="list-item-head">
                        <p class="list-item-title">${title}</p>
                        <p class="list-item-meta">${createdAt}</p>
                    </div>
                    <p class="list-item-meta">conversation_id=${conversationId}</p>
                    <p class="list-item-body">${rationale}</p>
                </article>
            `;
        })
        .join("");
}

async function fetchAuditLogs() {
    const payload = await requestJson(ENDPOINTS.auditLogs);
    renderAuditLogs(payload.logs || []);
}

async function fetchEvolutionSummary() {
    try {
        const payload = await requestJson(ENDPOINTS.evolutionSummary);
        nodes.evolutionPatterns.textContent = String(payload.total_patterns || 0);
        nodes.evolutionAnalyzed.textContent = String(payload.conversations_analyzed || 0);
        nodes.evolutionLatest.textContent = formatTime(payload.last_distilled_at);
        nodes.evolutionSummary.textContent = String(payload.summary || "no summary");
    } catch (error) {
        nodes.evolutionPatterns.textContent = "0";
        nodes.evolutionAnalyzed.textContent = "0";
        nodes.evolutionLatest.textContent = "--";
        nodes.evolutionSummary.textContent = `暫無資料: ${error.message}`;
    }
}

async function refreshAll() {
    setBusy(nodes.refreshAllBtn, true, "載入中...");
    try {
        await Promise.all([fetchHealthAndStatus(), fetchAuditLogs(), fetchEvolutionSummary()]);
        nodes.lastUpdated.textContent = `最後更新: ${formatTime(new Date().toISOString())}`;
    } catch (error) {
        nodes.lastUpdated.textContent = `更新失敗: ${error.message}`;
    } finally {
        setBusy(nodes.refreshAllBtn, false);
    }
}

function bindEvents() {
    nodes.refreshAllBtn?.addEventListener("click", refreshAll);
    nodes.saveTokenBtn?.addEventListener("click", async () => {
        state.readToken = String(nodes.readTokenInput?.value || "").trim();
        setStoredReadToken(state.readToken);
        renderAuthNote();
        await refreshAll();
    });
    nodes.clearTokenBtn?.addEventListener("click", async () => {
        state.readToken = "";
        if (nodes.readTokenInput) nodes.readTokenInput.value = "";
        setStoredReadToken("");
        renderAuthNote();
        await refreshAll();
    });
    nodes.readTokenInput?.addEventListener("keydown", async (event) => {
        if (event.key === "Enter") {
            state.readToken = String(nodes.readTokenInput?.value || "").trim();
            setStoredReadToken(state.readToken);
            renderAuthNote();
            await refreshAll();
        }
    });
}

async function initialize() {
    initializeToken();
    bindEvents();
    await refreshAll();
}

document.addEventListener("DOMContentLoaded", initialize);
