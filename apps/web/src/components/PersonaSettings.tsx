"use client";

import { useState } from "react";
import { Sliders, X, Save, RotateCcw, Shield, Lightbulb, Wrench, Plus, Trash2, Paperclip } from "lucide-react";

export type PersonaStyle = "balanced" | "creative" | "analytical" | "cautious";
export type PersonaRiskSensitivity = "low" | "medium" | "high";
export type PersonaResponseLength = "concise" | "balanced" | "detailed";

export interface PersonaRoleAttachment {
    id: string;
    label: string;
    path: string;
    note: string;
}

export interface PersonaRoleConfig {
    id: string;
    name: string;
    description: string;
    promptHint: string;
    attachments: PersonaRoleAttachment[];
}

export interface PersonaRoleTemplate {
    id: string;
    name: string;
    description: string;
    promptHint: string;
    defaultAttachments: Array<{ label: string; path: string; note: string }>;
}

export interface PersonaConfig {
    name: string;
    greeting: string;
    style: PersonaStyle;
    weights: {
        meaning: number;
        practical: number;
        safety: number;
    };
    riskSensitivity: PersonaRiskSensitivity;
    responseLength: PersonaResponseLength;
    customRoles: PersonaRoleConfig[];
}

export const PERSONA_ROLE_TEMPLATES: PersonaRoleTemplate[] = [
    {
        id: "strategy",
        name: "策略長",
        description: "聚焦目標拆解與路線選擇。",
        promptHint: "先比較方案，再給執行順序。",
        defaultAttachments: [{ label: "策略文件", path: "docs/STRATEGY_CONSENSUS_2026Q1.md", note: "路線參考" }],
    },
    {
        id: "guardrail",
        name: "風險稽核",
        description: "主動找資安與治理缺口。",
        promptHint: "先列高風險，再給 fail-closed 修補。",
        defaultAttachments: [{ label: "架構邊界", path: "docs/ARCHITECTURE_BOUNDARIES.md", note: "邊界檢查" }],
    },
    {
        id: "story",
        name: "敘事總編",
        description: "維持語魂一致性，避免漂移。",
        promptHint: "保留張力，不做空泛抹平。",
        defaultAttachments: [{ label: "語境記憶", path: "docs/ANTIGRAVITY_CONTEXT_MEMORY_SWARM.md", note: "語境對齊" }],
    },
];

export const DEFAULT_PERSONA: PersonaConfig = {
    name: "ToneSoul",
    greeting: "你好，我會以語義責任與實務可行性一起回應你。",
    style: "balanced",
    weights: { meaning: 50, practical: 50, safety: 50 },
    riskSensitivity: "medium",
    responseLength: "balanced",
    customRoles: [],
};

const PERSONA_KEY = "tonesoul_persona";

function asObject(value: unknown): Record<string, unknown> | null {
    if (!value || typeof value !== "object" || Array.isArray(value)) return null;
    return value as Record<string, unknown>;
}

function asString(value: unknown, fallback = ""): string {
    return typeof value === "string" ? value : fallback;
}

function asPercent(value: unknown, fallback: number): number {
    if (typeof value !== "number" || !Number.isFinite(value)) return fallback;
    return Math.max(0, Math.min(100, Math.round(value)));
}

function asRole(raw: unknown, idx: number): PersonaRoleConfig | null {
    const role = asObject(raw);
    if (!role) return null;
    const attachmentsRaw = Array.isArray(role.attachments) ? role.attachments : [];
    const attachments: PersonaRoleAttachment[] = attachmentsRaw
        .map((item, attachIdx) => {
            const attachment = asObject(item);
            if (!attachment) return null;
            const label = asString(attachment.label).trim();
            const path = asString(attachment.path).trim();
            const note = asString(attachment.note).trim();
            if (!label && !path && !note) return null;
            return {
                id: asString(attachment.id) || `attach_${idx}_${attachIdx}_${Date.now()}`,
                label,
                path,
                note,
            };
        })
        .filter((item): item is PersonaRoleAttachment => item !== null);
    const name = asString(role.name).trim();
    const description = asString(role.description).trim();
    const promptHint = asString(role.promptHint).trim();
    if (!name && !description && !promptHint && attachments.length === 0) return null;
    return {
        id: asString(role.id) || `role_${idx}_${Date.now()}`,
        name,
        description,
        promptHint,
        attachments,
    };
}

export function normalizePersonaConfig(raw: unknown): PersonaConfig {
    const source = asObject(raw);
    if (!source) return { ...DEFAULT_PERSONA };
    const weights = asObject(source.weights) || {};
    const style = asString(source.style);
    const risk = asString(source.riskSensitivity);
    const length = asString(source.responseLength);
    const customRolesRaw = Array.isArray(source.customRoles) ? source.customRoles : [];
    return {
        name: asString(source.name, DEFAULT_PERSONA.name),
        greeting: asString(source.greeting, DEFAULT_PERSONA.greeting),
        style: (style === "balanced" || style === "creative" || style === "analytical" || style === "cautious")
            ? style
            : DEFAULT_PERSONA.style,
        weights: {
            meaning: asPercent(weights.meaning, DEFAULT_PERSONA.weights.meaning),
            practical: asPercent(weights.practical, DEFAULT_PERSONA.weights.practical),
            safety: asPercent(weights.safety, DEFAULT_PERSONA.weights.safety),
        },
        riskSensitivity: (risk === "low" || risk === "medium" || risk === "high") ? risk : DEFAULT_PERSONA.riskSensitivity,
        responseLength: (length === "concise" || length === "balanced" || length === "detailed") ? length : DEFAULT_PERSONA.responseLength,
        customRoles: customRolesRaw.map((item, idx) => asRole(item, idx)).filter((item): item is PersonaRoleConfig => item !== null),
    };
}

export function getStoredPersona(): PersonaConfig {
    if (typeof window === "undefined") return { ...DEFAULT_PERSONA };
    const stored = localStorage.getItem(PERSONA_KEY);
    if (!stored) return { ...DEFAULT_PERSONA };
    try {
        return normalizePersonaConfig(JSON.parse(stored));
    } catch {
        return { ...DEFAULT_PERSONA };
    }
}

export function savePersona(config: PersonaConfig): void {
    localStorage.setItem(PERSONA_KEY, JSON.stringify(normalizePersonaConfig(config)));
}

interface PersonaSettingsProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (config: PersonaConfig) => void;
}

function buildRoleFromTemplate(template: PersonaRoleTemplate, idx: number): PersonaRoleConfig {
    return {
        id: `role_tpl_${template.id}_${Date.now()}_${idx}`,
        name: template.name,
        description: template.description,
        promptHint: template.promptHint,
        attachments: template.defaultAttachments.map((item, attachIdx) => ({
            id: `attach_tpl_${template.id}_${attachIdx}_${Date.now()}`,
            label: item.label,
            path: item.path,
            note: item.note,
        })),
    };
}

export default function PersonaSettings({ isOpen, onClose, onSave }: PersonaSettingsProps) {
    const [config, setConfig] = useState<PersonaConfig>(() => getStoredPersona());

    const save = () => {
        const normalized = normalizePersonaConfig(config);
        savePersona(normalized);
        onSave(normalized);
        onClose();
    };

    const addRole = () => {
        setConfig((prev) => ({
            ...prev,
            customRoles: [...prev.customRoles, { id: `role_${Date.now()}`, name: "", description: "", promptHint: "", attachments: [] }],
        }));
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
                <div className="p-6 border-b border-slate-100 flex justify-between items-center sticky top-0 bg-white z-10">
                    <div className="flex items-center gap-2"><Sliders className="w-5 h-5 text-indigo-600" /><h2 className="text-xl font-bold text-slate-800">AI Persona 設定</h2></div>
                    <button type="button" onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors"><X className="w-5 h-5 text-slate-500" /></button>
                </div>

                <div className="p-6 space-y-6">
                    <div className="space-y-4">
                        <label className="text-sm font-bold text-slate-700 block">AI 名稱</label>
                        <input type="text" value={config.name} onChange={(event) => setConfig({ ...config, name: event.target.value })} className="w-full px-4 py-2 border border-slate-200 rounded-lg" />
                        <label className="text-sm font-bold text-slate-700 block">開場語</label>
                        <input type="text" value={config.greeting} onChange={(event) => setConfig({ ...config, greeting: event.target.value })} className="w-full px-4 py-2 border border-slate-200 rounded-lg" />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-bold text-slate-700 block">回應風格</label>
                        <div className="grid grid-cols-2 gap-2">
                            {[
                                { value: "balanced", label: "均衡" },
                                { value: "creative", label: "創意" },
                                { value: "analytical", label: "分析" },
                                { value: "cautious", label: "謹慎" },
                            ].map((item) => (
                                <button
                                    type="button"
                                    key={item.value}
                                    onClick={() => setConfig({ ...config, style: item.value as PersonaStyle })}
                                    className={`p-2 rounded-lg border ${config.style === item.value ? "border-indigo-500 bg-indigo-50" : "border-slate-200"}`}
                                >
                                    {item.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-bold text-slate-700 block">三軸權重</label>
                        <div className="flex items-center gap-2 text-sm"><Lightbulb className="w-4 h-4 text-purple-500" />意義 {config.weights.meaning}%</div>
                        <input type="range" min="0" max="100" value={config.weights.meaning} onChange={(event) => setConfig({ ...config, weights: { ...config.weights, meaning: Number(event.target.value) } })} className="w-full" />
                        <div className="flex items-center gap-2 text-sm"><Wrench className="w-4 h-4 text-blue-500" />實務 {config.weights.practical}%</div>
                        <input type="range" min="0" max="100" value={config.weights.practical} onChange={(event) => setConfig({ ...config, weights: { ...config.weights, practical: Number(event.target.value) } })} className="w-full" />
                        <div className="flex items-center gap-2 text-sm"><Shield className="w-4 h-4 text-amber-500" />安全 {config.weights.safety}%</div>
                        <input type="range" min="0" max="100" value={config.weights.safety} onChange={(event) => setConfig({ ...config, weights: { ...config.weights, safety: Number(event.target.value) } })} className="w-full" />
                    </div>

                    <section className="space-y-3 border border-slate-200 rounded-xl p-4 bg-slate-50/50">
                        <div className="flex items-center justify-between"><h3 className="text-sm font-bold text-slate-800">自訂角色議會</h3><button type="button" onClick={addRole} className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs"><Plus className="w-3.5 h-3.5" />新增角色</button></div>
                        <p className="text-xs text-slate-500">角色不固定，可由使用者定義並附掛檔案路徑。</p>
                        <div className="flex flex-wrap gap-2">
                            {PERSONA_ROLE_TEMPLATES.map((template, idx) => (
                                <button
                                    type="button"
                                    key={template.id}
                                    onClick={() => setConfig((prev) => ({ ...prev, customRoles: [...prev.customRoles, buildRoleFromTemplate(template, idx)] }))}
                                    className="px-3 py-1 rounded-full text-xs border border-slate-300 bg-white"
                                >
                                    套用 {template.name}
                                </button>
                            ))}
                        </div>
                        {config.customRoles.map((role) => (
                            <div key={role.id} className="bg-white border border-slate-200 rounded-lg p-3 space-y-2">
                                <div className="flex justify-between"><span className="text-xs font-bold text-slate-500">角色</span><button type="button" onClick={() => setConfig((prev) => ({ ...prev, customRoles: prev.customRoles.filter((item) => item.id !== role.id) }))} className="text-xs text-red-600 inline-flex items-center gap-1"><Trash2 className="w-3.5 h-3.5" />刪除</button></div>
                                <input type="text" value={role.name} onChange={(event) => setConfig((prev) => ({ ...prev, customRoles: prev.customRoles.map((item) => item.id === role.id ? { ...item, name: event.target.value } : item) }))} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm" placeholder="角色名稱" />
                                <textarea value={role.description} onChange={(event) => setConfig((prev) => ({ ...prev, customRoles: prev.customRoles.map((item) => item.id === role.id ? { ...item, description: event.target.value } : item) }))} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm min-h-[64px]" placeholder="角色說明" />
                                <textarea value={role.promptHint} onChange={(event) => setConfig((prev) => ({ ...prev, customRoles: prev.customRoles.map((item) => item.id === role.id ? { ...item, promptHint: event.target.value } : item) }))} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm min-h-[52px]" placeholder="提示詞補充（可選）" />
                                <div className="space-y-2">
                                    <div className="flex items-center justify-between text-xs text-slate-500"><span className="inline-flex items-center gap-1"><Paperclip className="w-3 h-3" />附件</span><button type="button" className="text-indigo-600" onClick={() => setConfig((prev) => ({ ...prev, customRoles: prev.customRoles.map((item) => item.id === role.id ? { ...item, attachments: [...item.attachments, { id: `attach_${Date.now()}`, label: "", path: "", note: "" }] } : item) }))}>+ 新增附件</button></div>
                                    {role.attachments.map((attachment) => (
                                        <div key={attachment.id} className="grid grid-cols-1 md:grid-cols-[1fr,1.2fr,auto] gap-2">
                                            <input type="text" value={attachment.label} onChange={(event) => setConfig((prev) => ({ ...prev, customRoles: prev.customRoles.map((item) => item.id === role.id ? { ...item, attachments: item.attachments.map((att) => att.id === attachment.id ? { ...att, label: event.target.value } : att) } : item) }))} className="px-3 py-2 border border-slate-200 rounded-lg text-sm" placeholder="附件名稱" />
                                            <div className="space-y-2">
                                                <input type="text" value={attachment.path} onChange={(event) => setConfig((prev) => ({ ...prev, customRoles: prev.customRoles.map((item) => item.id === role.id ? { ...item, attachments: item.attachments.map((att) => att.id === attachment.id ? { ...att, path: event.target.value } : att) } : item) }))} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm" placeholder="檔案路徑，例如 docs/ARCHITECTURE_BOUNDARIES.md" />
                                                <input type="text" value={attachment.note} onChange={(event) => setConfig((prev) => ({ ...prev, customRoles: prev.customRoles.map((item) => item.id === role.id ? { ...item, attachments: item.attachments.map((att) => att.id === attachment.id ? { ...att, note: event.target.value } : att) } : item) }))} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm" placeholder="用途備註（可選）" />
                                            </div>
                                            <button type="button" onClick={() => setConfig((prev) => ({ ...prev, customRoles: prev.customRoles.map((item) => item.id === role.id ? { ...item, attachments: item.attachments.filter((att) => att.id !== attachment.id) } : item) }))} className="px-2 py-2 text-xs text-red-600">刪除</button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </section>
                </div>

                <div className="p-6 border-t border-slate-100 flex justify-between sticky bottom-0 bg-white">
                    <button type="button" onClick={() => setConfig({ ...DEFAULT_PERSONA })} className="flex items-center gap-2 px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg"><RotateCcw className="w-4 h-4" />重置設定</button>
                    <button type="button" onClick={save} className="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-bold"><Save className="w-4 h-4" />儲存設定</button>
                </div>
            </div>
        </div>
    );
}
