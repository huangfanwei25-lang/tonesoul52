// src/modules/EmbeddingProvider/embeddingProvider.ts

/**
 * @interface EmbeddingProvider
 * @description 定義一個語義嵌入提供者介面。
 * 實現此介面的類別將負責將文本轉換為數值向量 (embedding)。
 * 透過這個介面，我們可以輕鬆地替換不同的嵌入服務（例如 OpenAI, Cohere 等），
 * 而無需修改 SemanticVowMatcher 的核心邏輯。
 */
export interface EmbeddingProvider {
  /**
   * @method getEmbedding
   * @description 將給定文本轉換為語義向量。
   * @param {string} text - 要嵌入的文本。
   * @returns {Promise<number[]>} - 包含語義向量的 Promise。
   */
  getEmbedding(text: string): Promise<number[]>;
}

/**
 * @class OpenAIEmbeddingProvider
 * @description 實現 EmbeddingProvider 介面，使用 OpenAI 的嵌入服務。
 * ⚠️ 在實際運行中，需要配置 API Key 和正確的 URL。
 */
export class OpenAIEmbeddingProvider implements EmbeddingProvider {
  private apiKey: string;
  private modelId: string;

  constructor(apiKey: string, modelId: string = "text-embedding-ada-002") {
    this.apiKey = apiKey;
    this.modelId = modelId;
  }

  async getEmbedding(text: string): Promise<number[]> {
    try {
      const response = await fetch("https://api.openai.com/v1/embeddings", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${this.apiKey}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          input: text,
          model: this.modelId
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`OpenAI API error: ${response.status} - ${errorData.error.message}`);
      }

      const json = await response.json();
      return json.data[0].embedding;
    } catch (error) {
      console.error("Error calling OpenAI Embedding API:", error);
      throw error;
    }
  }
}

/**
 * @class MockEmbeddingProvider
 * @description 實現 EmbeddingProvider 介面，用於測試和開發。
 * 它不進行實際 API 調用，而是根據關鍵字返回模擬的語義向量。
 * 這對於在沒有 API Key 或網路連接的環境下進行單元測試非常有用。
 */
export class MockEmbeddingProvider implements EmbeddingProvider {
  async getEmbedding(text: string): Promise<number[]> {
    // ⚠️ 這是模擬實現。實際需要調用 NLP 嵌入服務
    // 這裡簡單地為常見模式返回虛擬向量
    if (text.includes("多個角度") || text.includes("很複雜") || text.includes("或許")) {
      return Promise.resolve([0.1, 0.2, 0.3]); // 迴避性
    }
    if (text.includes("我認為") || text.includes("坦白地說")) {
      return Promise.resolve([0.9, 0.8, 0.7]); // 直率性
    }
    if (text.includes("承認") || text.includes("我會負責")) {
      return Promise.resolve([0.7, 0.7, 0.9]); // 負責性
    }
    return Promise.resolve([0.5, 0.5, 0.5]); // 預設中立
  }
}
