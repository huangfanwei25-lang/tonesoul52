"use client";

import { useState } from "react";
import { Download, Upload, Database, X, Check, AlertTriangle } from "lucide-react";
import {
    Conversation,
    MemoryInsight,
    getConversations,
    getAllMemoryInsights,
    saveConversation,
    saveMemoryInsight
} from "@/lib/db";

interface DataManagerProps {
    isOpen: boolean;
    onClose: () => void;
    onDataImported: () => void;
}

interface ExportData {
    version: string;
    exportedAt: string;
    conversations: Conversation[];
    memories: MemoryInsight[];
}

export default function DataManager({ isOpen, onClose, onDataImported }: DataManagerProps) {
    const [isExporting, setIsExporting] = useState(false);
    const [isImporting, setIsImporting] = useState(false);
    const [status, setStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

    // 導出所有數據
    const handleExport = async () => {
        setIsExporting(true);
        setStatus(null);

        try {
            const conversations = await getConversations();
            const memories = await getAllMemoryInsights();

            const exportData: ExportData = {
                version: "1.0.0",
                exportedAt: new Date().toISOString(),
                conversations,
                memories
            };

            // 創建下載
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `tonesoul_backup_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            setStatus({
                type: 'success',
                message: `成功導出 ${conversations.length} 個對話和 ${memories.length} 條記憶`
            });
        } catch (err) {
            console.error('Export failed:', err);
            setStatus({ type: 'error', message: '導出失敗' });
        } finally {
            setIsExporting(false);
        }
    };

    // 導入數據
    const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setIsImporting(true);
        setStatus(null);

        try {
            const text = await file.text();
            const data = JSON.parse(text) as ExportData;

            // 驗證格式
            if (!data.version || !data.conversations || !data.memories) {
                throw new Error('無效的備份文件格式');
            }

            // 導入對話
            let importedConvs = 0;
            for (const conv of data.conversations) {
                await saveConversation(conv);
                importedConvs++;
            }

            // 導入記憶
            let importedMemories = 0;
            for (const memory of data.memories) {
                await saveMemoryInsight(memory);
                importedMemories++;
            }

            setStatus({
                type: 'success',
                message: `成功導入 ${importedConvs} 個對話和 ${importedMemories} 條記憶`
            });

            // 通知父組件刷新數據
            onDataImported();
        } catch (err) {
            console.error('Import failed:', err);
            setStatus({
                type: 'error',
                message: err instanceof Error ? err.message : '導入失敗'
            });
        } finally {
            setIsImporting(false);
            // 清除 file input
            event.target.value = '';
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
                {/* Header */}
                <div className="p-6 border-b border-slate-100 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <Database className="w-5 h-5 text-indigo-600" />
                        <h2 className="text-xl font-bold text-slate-800">數據管理</h2>
                    </div>
                    <button type="button" onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors">
                        <X className="w-5 h-5 text-slate-500" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Export Section */}
                    <div className="p-4 border border-slate-200 rounded-xl">
                        <h3 className="font-bold text-slate-800 mb-2 flex items-center gap-2">
                            <Download className="w-4 h-4 text-emerald-500" />
                            導出備份
                        </h3>
                        <p className="text-sm text-slate-500 mb-4">
                            將所有對話記錄和記憶洞察導出為 JSON 文件
                        </p>
                        <button type="button"
                            onClick={handleExport}
                            disabled={isExporting}
                            className="w-full py-2 px-4 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                        >
                            {isExporting ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                    導出中...
                                </>
                            ) : (
                                <>
                                    <Download className="w-4 h-4" />
                                    導出數據
                                </>
                            )}
                        </button>
                    </div>

                    {/* Import Section */}
                    <div className="p-4 border border-slate-200 rounded-xl">
                        <h3 className="font-bold text-slate-800 mb-2 flex items-center gap-2">
                            <Upload className="w-4 h-4 text-blue-500" />
                            導入備份
                        </h3>
                        <p className="text-sm text-slate-500 mb-4">
                            從備份文件恢復對話記錄和記憶洞察
                        </p>
                        <label className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors cursor-pointer flex items-center justify-center gap-2">
                            {isImporting ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                    導入中...
                                </>
                            ) : (
                                <>
                                    <Upload className="w-4 h-4" />
                                    選擇文件導入
                                </>
                            )}
                            <input
                                type="file"
                                accept=".json"
                                onChange={handleImport}
                                disabled={isImporting}
                                className="hidden"
                            />
                        </label>
                    </div>

                    {/* Status Message */}
                    {status && (
                        <div className={`p-4 rounded-lg flex items-center gap-2 ${status.type === 'success'
                                ? 'bg-emerald-50 text-emerald-700'
                                : 'bg-red-50 text-red-700'
                            }`}>
                            {status.type === 'success' ? (
                                <Check className="w-5 h-5" />
                            ) : (
                                <AlertTriangle className="w-5 h-5" />
                            )}
                            <span>{status.message}</span>
                        </div>
                    )}

                    {/* Info */}
                    <p className="text-xs text-slate-400 text-center">
                        💡 備份文件可以在不同設備間傳輸，實現數據同步
                    </p>
                </div>
            </div>
        </div>
    );
}

