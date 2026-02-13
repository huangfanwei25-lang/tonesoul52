import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "隱私政策 | ToneSoul",
  description: "ToneSoul 資料收集、儲存、同意與刪除機制說明。",
};

const sections = [
  {
    title: "1. 我們收集什麼",
    body: [
      "對話內容（使用者輸入與 AI 回覆）",
      "會話識別（session_id、conversation_id）",
      "必要的審計欄位（例如 gate decision、張力指標、時間戳記）",
    ],
  },
  {
    title: "2. 資料如何儲存",
    body: [
      "前端資料：主要儲存在瀏覽器本地 IndexedDB 與 localStorage。",
      "後端資料：若啟用持久化，對話與審計資料會寫入 Supabase（conversations/messages/audit_logs/soul_memories）。",
      "你可以隨時撤回同意並要求刪除已記錄資料。",
    ],
  },
  {
    title: "3. API Key 與敏感資訊",
    body: [
      "使用者在前端輸入的 API Key 只存於本地（localStorage）。",
      "前端不會把 API Key 回傳到 ToneSoul 後端，也不會寫入後端審計日誌。",
      "請避免在對話中輸入密碼、金鑰或其他不必要的個資。",
    ],
  },
  {
    title: "4. 資料用途",
    body: [
      "維持系統運作與對話品質（例如審議、安全決策、回應追蹤）。",
      "進行匿名化後的品質分析與模型治理研究。",
      "不將可識別個資出售給第三方廣告平台。",
    ],
  },
  {
    title: "5. 同意撤回與刪除",
    body: [
      "前端可透過同意撤回流程觸發刪除。",
      "後端提供刪除入口：DELETE /api/consent/<session_id>。",
      "完成刪除後，系統會回傳 deletion_report（包含刪除筆數摘要）。",
    ],
  },
  {
    title: "6. 前後端分工",
    body: [
      "前端是使用者服務：重點是可視化與交互。",
      "後端是 AI 服務：重點是審議、記憶、審計、演化處理。",
      "這份分工是資料流與權責邊界的基礎。",
    ],
  },
];

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-4xl px-6 py-12">
        <header className="mb-10">
          <p className="text-xs uppercase tracking-[0.24em] text-sky-300/80">
            ToneSoul Privacy
          </p>
          <h1 className="mt-3 text-3xl font-bold md:text-4xl">隱私政策</h1>
          <p className="mt-4 text-sm text-slate-300">
            最後更新：2026-02-13。此頁內容對齊 `docs/privacy_policy.md` 與部署架構 v2.0。
          </p>
          <div className="mt-6 flex flex-wrap gap-3 text-sm">
            <Link
              href="/"
              className="rounded-lg border border-slate-700 bg-slate-900/70 px-4 py-2 hover:border-sky-400"
            >
              回到 App
            </Link>
            <Link
              href="/docs"
              className="rounded-lg border border-slate-700 bg-slate-900/70 px-4 py-2 hover:border-sky-400"
            >
              查看文件
            </Link>
          </div>
        </header>

        <section className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h2 className="text-lg font-semibold text-sky-200">快速摘要</h2>
          <ul className="list-disc space-y-2 pl-5 text-sm text-slate-300">
            <li>前端資料預設在本地儲存；後端持久化由部署設定決定。</li>
            <li>API Key 僅在前端保存，不會由後端代管。</li>
            <li>你可以透過同意撤回流程要求資料刪除。</li>
          </ul>
        </section>

        <div className="mt-8 space-y-6">
          {sections.map((section) => (
            <section
              key={section.title}
              className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6"
            >
              <h2 className="text-lg font-semibold text-white">{section.title}</h2>
              <ul className="mt-4 list-disc space-y-2 pl-5 text-sm text-slate-300">
                {section.body.map((line) => (
                  <li key={line}>{line}</li>
                ))}
              </ul>
            </section>
          ))}
        </div>

        <footer className="mt-10 rounded-2xl border border-slate-800 bg-slate-900/60 p-6 text-sm text-slate-300">
          若你對隱私條款有疑問，請先檢視 `docs/privacy_policy.md`，再透過專案維護管道回報。
        </footer>
      </div>
    </main>
  );
}
