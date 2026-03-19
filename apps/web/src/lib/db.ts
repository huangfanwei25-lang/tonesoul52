/**
 * ToneSoul IndexedDB Storage Layer
 * 
 * 提供本地對話儲存，不需要登入或後端。
 * 資料存在用戶的瀏覽器中。
 */

const DB_NAME = 'tonesoul_db';
const DB_VERSION = 2; // v2: added memory_insights store
const STORE_NAME = 'conversations';
const MEMORY_STORE_NAME = 'memory_insights';
const MAX_CONVERSATIONS = 10;
const MAX_MEMORIES = 50;

export interface GovernanceBrief {
    verdict?: string;
    responsibility_tier?: string;
    uncertainty_band?: number | null;
    coherence?: number | null;
    soul_passed?: boolean | null;
    contradiction_count?: number;
    strategy?: string;
    divergence_band?: string;
    dispatch_state?: string;
    next_focus?: string;
}

export interface LifeEntryBrief {
    response_summary?: string;
    inner_intent?: string;
    strategy?: string;
    persona_mode?: string;
    trajectory_label?: string;
    self_commit_count?: number;
    rupture_count?: number;
    emergent_value_count?: number;
}

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    deliberation?: DeliberationData;
    deliberation_level?: 'mock' | 'runtime';
    backend_mode?: string;
    execution_profile?: 'interactive' | 'engineering';
    fallback_metadata?: {
        triggered: boolean;
        reason: string;
        execution_profile?: 'interactive' | 'engineering';
    };
    distillation_guard?: {
        score: number;
        level: 'low' | 'medium' | 'high';
        policy_action: 'normal' | 'reduce_detail' | 'constrain_reasoning';
        signals: string[];
    };
    governance_brief?: GovernanceBrief;
    life_entry_brief?: LifeEntryBrief;
    timestamp: number;
}

export interface DeliberationData {
    council_chamber?: {
        philosopher: { internal_monologue?: string; self_diagnosed_tension?: number; stance: string; conflict_point?: string; benevolence_check?: string };
        engineer: { internal_monologue?: string; self_diagnosed_tension?: number; stance: string; conflict_point?: string; benevolence_check?: string };
        guardian: { internal_monologue?: string; self_diagnosed_tension?: number; stance: string; conflict_point?: string; benevolence_check?: string };
    };
    quality?: {
        score: number;
        band: 'low' | 'medium' | 'high';
    };
    entropy_meter?: {
        value: number;
        status: string;
        calculation_note?: string;
    };
    decision_matrix?: {
        user_hidden_intent: string;
        ai_strategy_name: string;
        intended_effect: string;
        tone_tag: string;
    };
    audit?: {
        honesty_score: number;
        responsibility_check: string;
        audit_verdict: string;
        // 程式碼驗證（可追溯）
        code_validation?: {
            code_honesty_score: number;
            discrepancy: number;
            flags: string[];
            is_valid: boolean;
        };
    };
    role_tensions?: Array<{
        from: string;
        from_role: string;
        to: string;
        to_role: string;
        reason: string;
        counter_reason: string;
        evidence: string[];
    }>;
    recommended_action?: string;
    visual_context?: string;

    // ==================== vMT-2601 Multiplex Thinking ====================
    // 參考論文：Multiplex Thinking: Reasoning via Token-wise Branch-and-Merge
    // 公式：h_multiplex = Σ w_i · E(t_i)
    multiplex_conclusion?: {
        // 主要路徑（最高權重）
        primary_path: {
            source: 'philosopher' | 'engineer' | 'guardian';
            weight: number;           // w_primary ∈ [0, 1]
            reasoning: string;        // 為何此路徑獲得最高權重
        };
        // 邏輯陰影（被淘汰但保留的路徑）
        shadows: Array<{
            source: 'philosopher' | 'engineer' | 'guardian';
            weight: number;           // w_shadow ∈ [0, 1]
            conflict_reason: string;  // 與 primary 的衝突點
            recovery_condition: string; // 什麼情況下此路徑會變正確
            collapse_cost: string;    // 強行坍縮會犧牲什麼資訊
        }>;
        // 張力狀態（自適應熵）
        tension: {
            level: 'LOW' | 'MEDIUM' | 'HIGH';
            // 公式：如果 w_max > 0.7 → LOW, 0.5-0.7 → MEDIUM, < 0.5 → HIGH
            formula_ref: string;      // 計算公式參照
            weight_distribution: string; // 例如 "0.5 / 0.3 / 0.2"
        };
        // 合併策略
        merge_strategy: 'COLLAPSE' | 'PRESERVE_SHADOWS' | 'EXPLICIT_CONFLICT';
        merge_note: string;
    };
    semantic_contradictions?: Array<Record<string, unknown>>;
    semantic_graph_summary?: Record<string, unknown>;
    visual_chain_snapshot?: {
        frame_id?: string;
        frame_type?: string;
        title?: string;
        created_at?: string;
        branch?: string;
        tags?: string[];
        data?: Record<string, unknown>;
        mermaid?: string;
    };
    final_synthesis?: {
        response_text: string;
    };
    next_moves?: Array<{ label: string; text: string }>;
    // Soul Auditor 審計結果
    soulAudit?: {
        passed: boolean;
        honestyScore: number;
        violations: number;
        auditNote: string;
    };
}

export interface Conversation {
    id: string;
    title: string;
    createdAt: number;
    updatedAt: number;
    messages: Message[];
}

// 記憶洞察（用於跨對話記憶注入）
export interface MemoryInsight {
    id: string;
    conversationId: string;
    createdAt: number;
    summary: string;           // 對話摘要
    keyInsights: string[];     // 關鍵洞察
    emotionalArc: string;      // 情緒弧線
    hiddenNeeds: string;       // 用戶潛在需求
    topics: string[];          // 話題標籤（用於相關性搜尋）
    messageCount: number;      // 對話訊息數
}

let dbInstance: IDBDatabase | null = null;

/**
 * 初始化 IndexedDB
 */
export async function initDB(): Promise<IDBDatabase> {
    if (dbInstance) return dbInstance;

    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);

        request.onerror = () => reject(request.error);

        request.onsuccess = () => {
            dbInstance = request.result;
            resolve(dbInstance);
        };

        request.onupgradeneeded = (event) => {
            const db = (event.target as IDBOpenDBRequest).result;

            // v1: conversations store
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                const store = db.createObjectStore(STORE_NAME, { keyPath: 'id' });
                store.createIndex('updatedAt', 'updatedAt', { unique: false });
                store.createIndex('createdAt', 'createdAt', { unique: false });
            }

            // v2: memory_insights store
            if (!db.objectStoreNames.contains(MEMORY_STORE_NAME)) {
                const memoryStore = db.createObjectStore(MEMORY_STORE_NAME, { keyPath: 'id' });
                memoryStore.createIndex('conversationId', 'conversationId', { unique: false });
                memoryStore.createIndex('createdAt', 'createdAt', { unique: false });
            }
        };
    });
}

/**
 * 取得所有對話（按更新時間倒序）
 */
export async function getConversations(): Promise<Conversation[]> {
    const db = await initDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, 'readonly');
        const store = tx.objectStore(STORE_NAME);
        const request = store.getAll();

        request.onsuccess = () => {
            const conversations = request.result as Conversation[];
            // 按更新時間倒序
            conversations.sort((a, b) => b.updatedAt - a.updatedAt);
            resolve(conversations);
        };
        request.onerror = () => reject(request.error);
    });
}

/**
 * 取得單一對話
 */
export async function getConversation(id: string): Promise<Conversation | null> {
    const db = await initDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, 'readonly');
        const store = tx.objectStore(STORE_NAME);
        const request = store.get(id);

        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject(request.error);
    });
}

/**
 * 儲存對話
 */
export async function saveConversation(conversation: Conversation): Promise<void> {
    const db = await initDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, 'readwrite');
        const store = tx.objectStore(STORE_NAME);

        conversation.updatedAt = Date.now();
        store.put(conversation);

        tx.oncomplete = () => {
            // 儲存後檢查對話數量限制
            enforceLimit(MAX_CONVERSATIONS);
            resolve();
        };
        tx.onerror = () => reject(tx.error);
    });
}

/**
 * 刪除對話
 */
export async function deleteConversation(id: string): Promise<void> {
    const db = await initDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, 'readwrite');
        const store = tx.objectStore(STORE_NAME);
        store.delete(id);

        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
    });
}

/**
 * 限制對話數量，刪除最舊的
 */
export async function enforceLimit(maxCount: number): Promise<void> {
    const conversations = await getConversations();

    if (conversations.length <= maxCount) return;

    // 刪除超出限制的舊對話
    const toDelete = conversations.slice(maxCount);
    for (const conv of toDelete) {
        await deleteConversation(conv.id);
    }
}

/**
 * 建立新對話
 */
export function createConversation(firstMessage?: string): Conversation {
    const now = Date.now();
    return {
        id: `conv_${now}_${Math.random().toString(36).substr(2, 9)}`,
        title: firstMessage?.slice(0, 50) || '新對話',
        createdAt: now,
        updatedAt: now,
        messages: [],
    };
}

/**
 * 新增訊息到對話
 */
export async function addMessageToConversation(
    conversationId: string,
    message: Message
): Promise<Conversation | null> {
    const conversation = await getConversation(conversationId);
    if (!conversation) return null;

    conversation.messages.push(message);

    // 如果是第一則用戶訊息，更新標題
    if (conversation.messages.length === 1 && message.role === 'user') {
        conversation.title = message.content.slice(0, 50);
        if (message.content.length > 50) {
            conversation.title += '...';
        }
    }

    await saveConversation(conversation);
    return conversation;
}

/**
 * 清除所有對話
 */
export async function clearAllConversations(): Promise<void> {
    const db = await initDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, 'readwrite');
        const store = tx.objectStore(STORE_NAME);
        store.clear();

        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
    });
}

/**
 * 清除所有記憶洞察
 */
export async function clearAllMemoryInsights(): Promise<void> {
    const db = await initDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction(MEMORY_STORE_NAME, 'readwrite');
        const store = tx.objectStore(MEMORY_STORE_NAME);
        store.clear();

        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
    });
}

// ==================== 記憶洞察 CRUD ====================

/**
 * 儲存記憶洞察
 */
export async function saveMemoryInsight(insight: MemoryInsight): Promise<void> {
    const db = await initDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction(MEMORY_STORE_NAME, 'readwrite');
        const store = tx.objectStore(MEMORY_STORE_NAME);
        store.put(insight);

        tx.oncomplete = async () => {
            // 限制記憶數量
            await enforceMemoryLimit(MAX_MEMORIES);
            resolve();
        };
        tx.onerror = () => reject(tx.error);
    });
}

/**
 * 取得所有記憶洞察（按時間倒序）
 */
export async function getAllMemoryInsights(): Promise<MemoryInsight[]> {
    const db = await initDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction(MEMORY_STORE_NAME, 'readonly');
        const store = tx.objectStore(MEMORY_STORE_NAME);
        const request = store.getAll();

        request.onsuccess = () => {
            const memories = request.result as MemoryInsight[];
            memories.sort((a, b) => b.createdAt - a.createdAt);
            resolve(memories);
        };
        request.onerror = () => reject(request.error);
    });
}

/**
 * 取得特定對話的記憶洞察
 */
export async function getMemoryByConversationId(conversationId: string): Promise<MemoryInsight | null> {
    const db = await initDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction(MEMORY_STORE_NAME, 'readonly');
        const store = tx.objectStore(MEMORY_STORE_NAME);
        const index = store.index('conversationId');
        const request = index.get(conversationId);

        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject(request.error);
    });
}

/**
 * 刪除記憶洞察
 */
export async function deleteMemoryInsight(id: string): Promise<void> {
    const db = await initDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction(MEMORY_STORE_NAME, 'readwrite');
        const store = tx.objectStore(MEMORY_STORE_NAME);
        store.delete(id);

        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
    });
}

/**
 * 限制記憶數量
 */
async function enforceMemoryLimit(maxCount: number): Promise<void> {
    const memories = await getAllMemoryInsights();

    if (memories.length <= maxCount) return;

    // 刪除最舊的記憶
    const toDelete = memories.slice(maxCount);
    for (const memory of toDelete) {
        await deleteMemoryInsight(memory.id);
    }
}

/**
 * 搜尋相關記憶（基於關鍵字匹配）
 */
export async function findRelevantMemories(
    query: string,
    maxCount: number = 3
): Promise<MemoryInsight[]> {
    const memories = await getAllMemoryInsights();

    // 簡單的關鍵字匹配
    const queryTokens = query.toLowerCase().split(/\s+/).filter(t => t.length > 1);

    const scored = memories.map(memory => {
        let score = 0;
        const allText = [
            memory.summary,
            memory.emotionalArc,
            memory.hiddenNeeds,
            ...memory.keyInsights,
            ...memory.topics
        ].join(' ').toLowerCase();

        for (const token of queryTokens) {
            if (allText.includes(token)) {
                score += 1;
            }
        }

        // 加分：新的記憶優先
        const ageInDays = (Date.now() - memory.createdAt) / (1000 * 60 * 60 * 24);
        const recencyBonus = Math.max(0, 1 - ageInDays / 30); // 30天內的記憶加分
        score += recencyBonus * 0.5;

        return { memory, score };
    });

    return scored
        .filter(s => s.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, maxCount)
        .map(s => s.memory);
}
