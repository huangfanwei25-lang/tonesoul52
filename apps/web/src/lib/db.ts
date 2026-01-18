/**
 * ToneSoul IndexedDB Storage Layer
 * 
 * 提供本地對話儲存，不需要登入或後端。
 * 資料存在用戶的瀏覽器中。
 */

const DB_NAME = 'tonesoul_db';
const DB_VERSION = 1;
const STORE_NAME = 'conversations';
const MAX_CONVERSATIONS = 10;

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    deliberation?: DeliberationData;
    timestamp: number;
}

export interface DeliberationData {
    council_chamber?: {
        philosopher: { stance: string; conflict_point?: string };
        engineer: { stance: string; conflict_point?: string };
        guardian: { stance: string; conflict_point?: string };
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
    final_synthesis?: {
        response_text: string;
    };
    next_moves?: Array<{ label: string; text: string }>;
}

export interface Conversation {
    id: string;
    title: string;
    createdAt: number;
    updatedAt: number;
    messages: Message[];
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

            if (!db.objectStoreNames.contains(STORE_NAME)) {
                const store = db.createObjectStore(STORE_NAME, { keyPath: 'id' });
                store.createIndex('updatedAt', 'updatedAt', { unique: false });
                store.createIndex('createdAt', 'createdAt', { unique: false });
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
