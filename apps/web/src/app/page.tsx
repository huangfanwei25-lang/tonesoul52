"use client";

import { useState, useEffect, useCallback, useSyncExternalStore } from "react";
import Link from "next/link";
import ConsentModal from "@/components/ConsentModal";
import ChatInterface from "@/components/ChatInterface";
import ConversationList from "@/components/ConversationList";
import SettingsModal, { ApiSettings, getStoredSettings } from "@/components/SettingsModal";
import LlmSwitcher from "@/components/LlmSwitcher";
import SessionReport from "@/components/SessionReport";
import EntropyChart from "@/components/EntropyChart";
import TensionTimeline from "@/components/TensionTimeline";
import DataManager from "@/components/DataManager";
import PersonaSettings, { PersonaConfig, getStoredPersona } from "@/components/PersonaSettings";
import TierModelPublicCue from "@/components/TierModelPublicCue";
import { SoulState, loadSoulState, getInitialSoulState } from "@/lib/soulEngine";
import OnboardingGuide, { hasCompletedOnboarding } from "@/components/OnboardingGuide";
import {
  Conversation,
  getConversations,
  createConversation,
  saveConversation,
  deleteConversation,
  clearAllConversations,
  clearAllMemoryInsights,
} from "@/lib/db";
import { Menu, Settings, FileText, LogOut, Key, Layers, BarChart3, Database, Sliders, BookOpen } from "lucide-react";

const RESETTABLE_LOCAL_STORAGE_KEYS = [
  "tonesoul_consent",
  "tonesoul_api_settings",
  "tonesoul_persona",
  "tonesoul_onboarded",
  "tonesoul_soul_state",
  "tonesoul_audit_log",
  "tonesoul.private_notes.v1",
  "tonesoul.chat.council_mode",
] as const;

export default function Home() {
  const isHydrated = useSyncExternalStore(
    () => () => { },
    () => true,
    () => false,
  );
  const [hasConsent, setHasConsent] = useState<boolean>(() => {
    if (typeof window === "undefined") return false;
    return localStorage.getItem("tonesoul_consent") === "true";
  });
  const [showSidebar, setShowSidebar] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [showReport, setShowReport] = useState(false);
  const [showDataManager, setShowDataManager] = useState(false);
  const [showPersonaSettings, setShowPersonaSettings] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(() => !hasCompletedOnboarding());
  const [apiSettings, setApiSettings] = useState<ApiSettings | null>(() => getStoredSettings());
  const [personaConfig, setPersonaConfig] = useState<PersonaConfig | null>(() => getStoredPersona());
  const [soulState] = useState<SoulState>(() => loadSoulState() || getInitialSoulState());

  // Conversation state
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);

  const loadConversations = useCallback(async () => {
    try {
      const convs = await getConversations();
      setConversations(convs);
      setCurrentConversation((prev) => {
        if (!prev) return convs[0] ?? null;
        const match = convs.find((c) => c.id === prev.id);
        return match ?? convs[0] ?? null;
      });
    } catch (error) {
      console.error("Failed to load conversations:", error);
    }
  }, []);

  // Load conversations from IndexedDB
  useEffect(() => {
    if (!isHydrated || !hasConsent) return;
    const timer = setTimeout(() => {
      void loadConversations();
    }, 0);
    return () => clearTimeout(timer);
  }, [isHydrated, hasConsent, loadConversations]);

  const handleAcceptConsent = async () => {
    setHasConsent(true);
    localStorage.setItem("tonesoul_consent", "true");
  };

  const handleDeclineConsent = () => {
    alert("需要同意才能使用本服務。");
  };

  const handleNewConversation = useCallback(async () => {
    const newConv = createConversation();
    await saveConversation(newConv);
    setConversations(prev => [newConv, ...prev]);
    setCurrentConversation(newConv);
    setShowSidebar(false); // Close sidebar on mobile
  }, []);

  const handleSelectConversation = useCallback((conv: Conversation) => {
    setCurrentConversation(conv);
    setShowSidebar(false); // Close sidebar on mobile
  }, []);

  const handleDeleteConversation = useCallback(
    async (id: string) => {
      try {
        await deleteConversation(id);
        await loadConversations();
      } catch (error) {
        console.error("Failed to delete conversation:", error);
        alert("刪除對話失敗，請稍後再試。");
      }
    },
    [loadConversations],
  );

  const handleConversationUpdate = useCallback((updatedConv: Conversation) => {
    setConversations(prev =>
      prev.map(c => c.id === updatedConv.id ? updatedConv : c)
        .sort((a, b) => b.updatedAt - a.updatedAt)
    );
    setCurrentConversation(updatedConv);
  }, []);

  const handleWithdrawConsent = async () => {
    if (!confirm("確定要撤回同意並刪除所有資料嗎？此操作不可逆。")) {
      return;
    }

    try {
      await Promise.all([
        clearAllConversations(),
        clearAllMemoryInsights(),
      ]);
      RESETTABLE_LOCAL_STORAGE_KEYS.forEach((key) => {
        localStorage.removeItem(key);
      });
      setHasConsent(false);
      setShowOnboarding(true);
      setConversations([]);
      setCurrentConversation(null);
    } catch (error) {
      console.error("Withdraw consent error:", error);
    }
  };

  if (!isHydrated) {
    return <div className="min-h-screen bg-slate-50" />;
  }

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
        className={`fixed inset-y-0 left-0 z-40 w-72 bg-slate-900 text-white transform transition-transform duration-300 flex flex-col ${showSidebar ? "translate-x-0" : "-translate-x-full"
          } md:relative md:translate-x-0`}
      >
        {/* Logo */}
        <div className="p-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-600 rounded-xl">
              <Layers className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-bold text-lg">ToneStream</h1>
              <p className="text-xs text-slate-400">v2.5 Council Edition</p>
            </div>
          </div>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-hidden flex flex-col">
          <div className="flex-1 overflow-y-auto">
            <ConversationList
              conversations={conversations}
              currentId={currentConversation?.id || null}
              onSelect={handleSelectConversation}
              onNew={handleNewConversation}
              onDelete={handleDeleteConversation}
            />
          </div>

          {/* Entropy Chart */}
          <div className="border-t border-slate-800">
            <EntropyChart conversation={currentConversation} />
          </div>

          {/* Tension Timeline */}
          <div className="border-t border-slate-800 p-3">
            <TensionTimeline soulState={soulState} />
          </div>
        </div>

        {/* Report & Settings Buttons */}
        <div className="p-3 border-t border-slate-800 space-y-2">
          {/* Report Button */}
          <button type="button"
            onClick={() => setShowReport(true)}
            disabled={!currentConversation || currentConversation.messages.length < 2}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <BarChart3 className="w-5 h-5" />
            <span>生成洞察報告</span>
          </button>

          {/* API Settings Button */}
          <button type="button"
            onClick={() => setShowSettings(true)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 transition-colors"
          >
            <Key className="w-5 h-5" />
            <span>API 設定</span>
            {apiSettings?.apiKey && <span className="ml-auto text-xs text-emerald-400">✓</span>}
          </button>

          {/* Data Manager Button */}
          <button type="button"
            onClick={() => setShowDataManager(true)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 transition-colors"
          >
            <Database className="w-5 h-5" />
            <span>數據管理</span>
          </button>

          {/* Persona Settings Button */}
          <button type="button"
            onClick={() => setShowPersonaSettings(true)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 transition-colors"
          >
            <Sliders className="w-5 h-5" />
            <span>AI 個人化</span>
            {personaConfig?.name && personaConfig.name !== 'ToneSoul' && (
              <span className="ml-auto text-xs text-purple-400">✓</span>
            )}
          </button>
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-slate-800 space-y-1">
          <Link
            href="/docs"
            className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-slate-800 transition-colors text-slate-400 hover:text-white text-sm"
          >
            <BookOpen className="w-4 h-4" />
            <span>關於作者與理論</span>
          </Link>
          <a
            href="https://vocus.cc/article/69a3e06efd897800015fd9bac"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-slate-800 transition-colors text-slate-400 hover:text-white text-sm"
            title="Declarative Resistance Manifesto"
          >
            <BookOpen className="w-4 h-4" />
            <span>Declarative Resistance Manifesto</span>
          </a>
          <a
            href="https://vocus.cc/user/684f4366fd89780001893a72"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-slate-800 transition-colors text-slate-400 hover:text-white text-sm"
            title="Vocus 個人頁"
          >
            <BookOpen className="w-4 h-4" />
            <span>Vocus 個人頁</span>
          </a>
          <a
            href="/privacy"
            className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-slate-800 transition-colors text-slate-400 hover:text-white text-sm"
          >
            <FileText className="w-4 h-4" />
            <span>隱私政策</span>
          </a>
          <button type="button"
            onClick={handleWithdrawConsent}
            className="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-red-900/50 transition-colors text-slate-400 hover:text-red-300 text-sm"
          >
            <LogOut className="w-4 h-4" />
            <span>撤回同意 & 刪除資料</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 px-4 py-3 flex items-center gap-4 shrink-0">
          <button type="button"
            onClick={() => setShowSidebar(!showSidebar)}
            className="md:hidden p-2 hover:bg-slate-100 rounded-lg"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex-1 min-w-0">
            <h2 className="font-semibold text-slate-800 truncate">
              {currentConversation?.title || "ToneSoul Navigator"}
            </h2>
            <p className="text-xs text-slate-400">
              {currentConversation
                ? `${currentConversation.messages.length} 則訊息`
                : "選擇或建立對話"}
            </p>
          </div>
          <LlmSwitcher />
          <button type="button"
            onClick={() => setShowSettings(true)}
            className={`p-2 hover:bg-slate-100 rounded-lg ${!apiSettings?.apiKey ? 'animate-pulse' : ''}`}
            title={apiSettings?.apiKey ? 'API 已設定' : '請設定 API Key'}
          >
            <Settings className={`w-5 h-5 ${apiSettings?.apiKey ? 'text-emerald-500' : 'text-amber-500'}`} />
          </button>
        </header>

        <div className="border-b border-slate-200 bg-slate-50 px-4 py-3">
          <TierModelPublicCue variant="compact" />
        </div>

        {/* Chat Interface */}
        <div className="flex-1 overflow-hidden">
          <ChatInterface
            conversation={currentConversation}
            apiSettings={apiSettings}
            personaConfig={personaConfig}
            onConversationUpdate={handleConversationUpdate}
          />
        </div>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <SettingsModal
          isOpen={showSettings}
          onClose={() => setShowSettings(false)}
          onSave={setApiSettings}
          currentSettings={apiSettings}
        />
      )}

      {/* Session Report Modal */}
      <SessionReport
        isOpen={showReport}
        onClose={() => setShowReport(false)}
        messages={currentConversation?.messages.map(m => ({ ...m, timestamp: m.timestamp })) || []}
        apiSettings={apiSettings}
        conversationId={currentConversation?.id || ''}
      />

      {/* Data Manager Modal */}
      <DataManager
        isOpen={showDataManager}
        onClose={() => setShowDataManager(false)}
        onDataImported={loadConversations}
      />

      {/* Persona Settings Modal */}
      {showPersonaSettings && (
        <PersonaSettings
          isOpen={showPersonaSettings}
          onClose={() => setShowPersonaSettings(false)}
          onSave={setPersonaConfig}
        />
      )}

      {/* Onboarding Guide */}
      <OnboardingGuide
        isOpen={showOnboarding}
        onComplete={() => setShowOnboarding(false)}
        onOpenSettings={() => setShowSettings(true)}
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

