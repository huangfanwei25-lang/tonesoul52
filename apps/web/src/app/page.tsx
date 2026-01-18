"use client";

import { useState, useEffect } from "react";
import ConsentModal from "@/components/ConsentModal";
import ChatInterface from "@/components/ChatInterface";
import SettingsModal, { ApiSettings, getStoredSettings } from "@/components/SettingsModal";
import { Brain, Menu, Settings, FileText, LogOut, Key } from "lucide-react";

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [hasConsent, setHasConsent] = useState<boolean>(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [showSidebar, setShowSidebar] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [apiSettings, setApiSettings] = useState<ApiSettings | null>(null);

  useEffect(() => {
    // Check for existing session
    const storedSession = localStorage.getItem("tonesoul_session");
    const storedConsent = localStorage.getItem("tonesoul_consent");

    if (storedSession && storedConsent === "true") {
      setSessionId(storedSession);
      setHasConsent(true);
    }

    // Load stored API settings
    const storedApiSettings = getStoredSettings();
    if (storedApiSettings) {
      setApiSettings(storedApiSettings);
    }
  }, []);

  const handleAcceptConsent = async (consentType: string) => {
    try {
      const response = await fetch("/api/consent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ consent_type: consentType }),
      });

      const data = await response.json();

      if (data.session_id) {
        setSessionId(data.session_id);
        setHasConsent(true);
        localStorage.setItem("tonesoul_session", data.session_id);
        localStorage.setItem("tonesoul_consent", "true");
      }
    } catch (error) {
      console.error("Consent error:", error);
    }
  };

  const handleDeclineConsent = () => {
    // Show a message or redirect
    alert("需要同意才能使用本服務。");
  };

  const handleNewConversation = async (): Promise<string> => {
    try {
      const response = await fetch("/api/conversation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });

      const data = await response.json();
      setConversationId(data.conversation_id);
      return data.conversation_id;
    } catch (error) {
      console.error("New conversation error:", error);
      throw error;
    }
  };

  const handleWithdrawConsent = async () => {
    if (!confirm("確定要撤回同意並刪除所有資料嗎？此操作不可逆。")) {
      return;
    }

    try {
      await fetch("/api/consent", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });

      localStorage.removeItem("tonesoul_session");
      localStorage.removeItem("tonesoul_consent");
      setSessionId(null);
      setHasConsent(false);
      setConversationId(null);
    } catch (error) {
      console.error("Withdraw consent error:", error);
    }
  };

  // Show consent modal if no consent
  if (!hasConsent) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-purple-900">
        <ConsentModal onAccept={handleAcceptConsent} onDecline={handleDeclineConsent} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-slate-900 text-white transform transition-transform duration-300 ${showSidebar ? "translate-x-0" : "-translate-x-full"
          } md:relative md:translate-x-0`}
      >
        <div className="p-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-600 rounded-xl">
              <Brain className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-bold text-lg">ToneSoul</h1>
              <p className="text-xs text-slate-400">Navigator v2.0</p>
            </div>
          </div>
        </div>

        <div className="p-4 space-y-2">
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 transition-colors">
            <Brain className="w-5 h-5" />
            <span>新對話</span>
          </button>
          <button
            onClick={() => setShowSettings(true)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 transition-colors"
          >
            <Key className="w-5 h-5" />
            <span>API 設定</span>
            {apiSettings?.apiKey && <span className="ml-auto text-xs text-emerald-400">✓</span>}
          </button>
        </div>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-800 space-y-2">
          <a
            href="/privacy"
            className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-slate-800 transition-colors text-slate-400 hover:text-white"
          >
            <FileText className="w-4 h-4" />
            <span className="text-sm">隱私政策</span>
          </a>
          <button
            onClick={handleWithdrawConsent}
            className="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-red-900/50 transition-colors text-slate-400 hover:text-red-300"
          >
            <LogOut className="w-4 h-4" />
            <span className="text-sm">撤回同意 & 刪除資料</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 px-4 py-3 flex items-center gap-4">
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="md:hidden p-2 hover:bg-slate-100 rounded-lg"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex-1">
            <h2 className="font-semibold text-slate-800">對話</h2>
            <p className="text-xs text-slate-400">
              {conversationId ? `ID: ${conversationId}` : "新對話"}
            </p>
          </div>
          <button
            onClick={() => setShowSettings(true)}
            className={`p-2 hover:bg-slate-100 rounded-lg ${!apiSettings?.apiKey ? 'animate-pulse' : ''}`}
            title={apiSettings?.apiKey ? 'API 已設定' : '請設定 API Key'}
          >
            <Settings className={`w-5 h-5 ${apiSettings?.apiKey ? 'text-emerald-500' : 'text-amber-500'}`} />
          </button>
        </header>

        {/* Chat Interface */}
        <ChatInterface
          sessionId={sessionId || ""}
          conversationId={conversationId}
          onNewConversation={handleNewConversation}
          apiSettings={apiSettings}
        />
      </div>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        onSave={setApiSettings}
        currentSettings={apiSettings}
      />

      {/* Overlay for mobile sidebar */}
      {showSidebar && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setShowSidebar(false)}
        />
      )}
    </div>
  );
}
