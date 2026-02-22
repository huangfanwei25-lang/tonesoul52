"use client";

import { useEffect, useRef, useState } from "react";
import { MessageSquare, Plus, Trash2, MoreVertical } from "lucide-react";
import { Conversation } from "@/lib/db";

interface ConversationListProps {
    conversations: Conversation[];
    currentId: string | null;
    onSelect: (conv: Conversation) => void;
    onNew: () => void;
    onDelete: (id: string) => Promise<void>;
}

export default function ConversationList({
    conversations,
    currentId,
    onSelect,
    onNew,
    onDelete,
}: ConversationListProps) {
    const [menuOpen, setMenuOpen] = useState<string | null>(null);
    const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);
    const rootRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        if (!menuOpen) return;

        const handleOutsideClick = (event: MouseEvent) => {
            const target = event.target;
            if (!(target instanceof Node)) return;
            if (!rootRef.current?.contains(target)) {
                setMenuOpen(null);
            }
        };

        document.addEventListener("mousedown", handleOutsideClick);
        return () => {
            document.removeEventListener("mousedown", handleOutsideClick);
        };
    }, [menuOpen]);

    const formatDate = (timestamp: number) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return "今天";
        if (diffDays === 1) return "昨天";
        if (diffDays < 7) return `${diffDays} 天前`;
        return date.toLocaleDateString("zh-TW", { month: "short", day: "numeric" });
    };

    const handleDeleteClick = (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        setConfirmDeleteId(id);
        setMenuOpen(null);
    };

    const confirmDelete = async (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        try {
            await onDelete(id);
        } catch (error) {
            console.error("Failed to delete conversation:", error);
            alert("刪除對話失敗，請稍後再試。");
        }
        setConfirmDeleteId(null);
    };

    const cancelDelete = (e: React.MouseEvent) => {
        e.stopPropagation();
        setConfirmDeleteId(null);
    };

    return (
        <div ref={rootRef} className="flex flex-col h-full">
            {/* 新對話按鈕 */}
            <div className="p-3">
                <button
                    type="button"
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
                                    type="button"
                                    aria-label="打開對話操作選單"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setMenuOpen(menuOpen === conv.id ? null : conv.id);
                                    }}
                                    className={`p-1 rounded transition-all ${menuOpen === conv.id
                                        ? "opacity-100 bg-slate-700"
                                        : "opacity-100 md:opacity-0 md:group-hover:opacity-100 hover:bg-slate-700"
                                        }`}
                                >
                                    <MoreVertical className="w-4 h-4 text-slate-400" />
                                </button>
                            </div>

                            {/* 刪除確認對話框 */}
                            {confirmDeleteId === conv.id && (
                                <div className="absolute right-2 top-10 z-20 bg-slate-800 border border-slate-700 rounded-lg shadow-xl p-3 min-w-[200px]">
                                    <p className="text-sm text-slate-300 mb-3 text-center">確定要刪除這個對話嗎？</p>
                                    <div className="flex gap-2">
                                        <button
                                            type="button"
                                            onClick={cancelDelete}
                                            className="flex-1 px-2 py-1.5 text-xs text-slate-400 hover:bg-slate-700 rounded transition-colors"
                                        >
                                            取消
                                        </button>
                                        <button
                                            type="button"
                                            onClick={(e) => confirmDelete(conv.id, e)}
                                            className="flex-1 px-2 py-1.5 text-xs text-white bg-red-500/80 hover:bg-red-500 rounded transition-colors"
                                        >
                                            刪除
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* 下拉選單 */}
                            {menuOpen === conv.id && !confirmDeleteId && (
                                <div className="absolute right-2 top-10 z-10 bg-slate-800 border border-slate-700 rounded-lg shadow-xl py-1 min-w-[120px]">
                                    <button
                                        type="button"
                                        aria-label="刪除對話"
                                        onClick={(e) => handleDeleteClick(conv.id, e)}
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
