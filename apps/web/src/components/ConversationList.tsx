"use client";

import { useState } from "react";
import { MessageSquare, Plus, Trash2, MoreVertical } from "lucide-react";
import { Conversation, deleteConversation } from "@/lib/db";

interface ConversationListProps {
    conversations: Conversation[];
    currentId: string | null;
    onSelect: (conv: Conversation) => void;
    onNew: () => void;
    onDelete: (id: string) => void;
}

export default function ConversationList({
    conversations,
    currentId,
    onSelect,
    onNew,
    onDelete,
}: ConversationListProps) {
    const [menuOpen, setMenuOpen] = useState<string | null>(null);

    const formatDate = (timestamp: number) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return "今天";
        if (diffDays === 1) return "昨天";
        if (diffDays < 7) return `${diffDays} 天前`;
        return date.toLocaleDateString("zh-TW", { month: "short", day: "numeric" });
    };

    const handleDelete = async (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        if (confirm("確定要刪除這個對話嗎？")) {
            await deleteConversation(id);
            onDelete(id);
        }
        setMenuOpen(null);
    };

    return (
        <div className="flex flex-col h-full">
            {/* 新對話按鈕 */}
            <div className="p-3">
                <button
                    onClick={onNew}
                    className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium transition-colors"
                >
                    <Plus className="w-4 h-4" />
                    <span>新對話</span>
                </button>
            </div>

            {/* 對話列表 */}
            <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-1">
                {conversations.length === 0 ? (
                    <div className="text-center py-8 text-slate-500 text-sm">
                        <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-30" />
                        <p>還沒有對話</p>
                    </div>
                ) : (
                    conversations.map((conv) => (
                        <div
                            key={conv.id}
                            onClick={() => onSelect(conv)}
                            className={`relative group p-3 rounded-xl cursor-pointer transition-all ${currentId === conv.id
                                    ? "bg-indigo-600/20 border border-indigo-500/30"
                                    : "hover:bg-slate-800/50 border border-transparent"
                                }`}
                        >
                            <div className="flex items-start gap-3">
                                <MessageSquare className={`w-4 h-4 mt-0.5 shrink-0 ${currentId === conv.id ? "text-indigo-400" : "text-slate-500"
                                    }`} />

                                <div className="flex-1 min-w-0">
                                    <p className={`text-sm font-medium truncate ${currentId === conv.id ? "text-white" : "text-slate-300"
                                        }`}>
                                        {conv.title}
                                    </p>
                                    <p className="text-xs text-slate-500 mt-0.5">
                                        {formatDate(conv.updatedAt)} · {conv.messages.length} 則訊息
                                    </p>
                                </div>

                                {/* 更多選項按鈕 */}
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setMenuOpen(menuOpen === conv.id ? null : conv.id);
                                    }}
                                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-slate-700 rounded transition-all"
                                >
                                    <MoreVertical className="w-4 h-4 text-slate-400" />
                                </button>
                            </div>

                            {/* 下拉選單 */}
                            {menuOpen === conv.id && (
                                <div className="absolute right-2 top-10 z-10 bg-slate-800 border border-slate-700 rounded-lg shadow-xl py-1 min-w-[120px]">
                                    <button
                                        onClick={(e) => handleDelete(conv.id, e)}
                                        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-red-500/10 transition-colors"
                                    >
                                        <Trash2 className="w-3.5 h-3.5" />
                                        <span>刪除對話</span>
                                    </button>
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>

            {/* 對話數量提示 */}
            {conversations.length > 0 && (
                <div className="px-3 pb-3">
                    <p className="text-xs text-slate-600 text-center">
                        {conversations.length}/10 個對話
                    </p>
                </div>
            )}
        </div>
    );
}
