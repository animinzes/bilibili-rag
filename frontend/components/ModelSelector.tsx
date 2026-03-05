"use client";

import { useState, useEffect } from "react";
import { modelApi, ModelInfo, ModelListResponse } from "@/lib/api";

interface ModelSelectorProps {
    onClose: () => void;
}

export default function ModelSelector({ onClose }: ModelSelectorProps) {
    const [data, setData] = useState<ModelListResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [switching, setSwitching] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<"llm" | "embedding" | "asr">("llm");

    useEffect(() => {
        loadModels();
    }, []);

    const loadModels = async () => {
        try {
            const res = await modelApi.getModels();
            setData(res);
        } catch (e) {
            console.error("Failed to load models:", e);
        } finally {
            setLoading(false);
        }
    };

    const handleSelectModel = async (modelType: string, modelId: string) => {
        setSwitching(modelType);
        try {
            const res = await modelApi.setModel(modelType, modelId);
            if (res.success) {
                setData(prev => prev ? {
                    ...prev,
                    current_llm: res.current.llm,
                    current_embedding: res.current.embedding,
                    current_asr: res.current.asr,
                } : null);
            } else {
                alert(res.message);
            }
        } catch (e) {
            console.error("Failed to set model:", e);
            alert("切换失败");
        } finally {
            setSwitching(null);
        }
    };

    const getCurrentModel = (type: string) => {
        if (!data) return "";
        switch (type) {
            case "llm": return data.current_llm;
            case "embedding": return data.current_embedding;
            case "asr": return data.current_asr;
            default: return "";
        }
    };

    const getModels = (type: string): ModelInfo[] => {
        if (!data) return [];
        switch (type) {
            case "llm": return data.llm_models;
            case "embedding": return data.embedding_models;
            case "asr": return data.asr_models;
            default: return [];
        }
    };

    const getTabLabel = (tab: string) => {
        switch (tab) {
            case "llm": return "对话模型";
            case "embedding": return "向量模型";
            case "asr": return "语音模型";
            default: return "";
        }
    };

    if (loading) {
        return (
            <div className="modal-backdrop" onClick={onClose}>
                <div className="modal-card" onClick={e => e.stopPropagation()}>
                    <div className="empty-state">
                        <div className="panel-subtitle">加载中...</div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="modal-backdrop" onClick={onClose}>
            <div className="organize-modal" onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="organize-header">
                    <div>
                        <h2 className="panel-title">模型选择</h2>
                        <div className="panel-subtitle">切换后将应用于新的对话</div>
                    </div>
                    <button onClick={onClose} className="btn-icon" title="关闭">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M18 6L6 18M6 6l12 12"/>
                        </svg>
                    </button>
                </div>

                {/* Tabs */}
                <div style={{ 
                    display: "flex", 
                    gap: "8px", 
                    padding: "4px", 
                    background: "rgba(27, 23, 19, 0.04)", 
                    borderRadius: "999px",
                    border: "1px solid var(--border)"
                }}>
                    {(["llm", "embedding", "asr"] as const).map(tab => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            style={{
                                flex: 1,
                                padding: "8px 16px",
                                borderRadius: "999px",
                                border: "none",
                                fontSize: "13px",
                                fontWeight: 600,
                                cursor: "pointer",
                                transition: "all 0.2s ease",
                                background: activeTab === tab 
                                    ? "linear-gradient(135deg, #d98b2b 0%, #b66b17 100%)" 
                                    : "transparent",
                                color: activeTab === tab ? "#fff8f0" : "var(--ink-soft)",
                                boxShadow: activeTab === tab ? "0 4px 12px rgba(217, 139, 43, 0.25)" : "none"
                            }}
                        >
                            {getTabLabel(tab)}
                        </button>
                    ))}
                </div>

                {/* Current model */}
                <div style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    padding: "14px 16px",
                    background: "rgba(47, 124, 120, 0.08)",
                    borderRadius: "var(--radius)",
                    border: "1px dashed rgba(47, 124, 120, 0.3)"
                }}>
                    <div style={{
                        width: "32px",
                        height: "32px",
                        borderRadius: "50%",
                        background: "linear-gradient(135deg, var(--teal), #1f5b57)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "#fff",
                        fontSize: "14px"
                    }}>
                        ✓
                    </div>
                    <div style={{ flex: 1 }}>
                        <div style={{ fontSize: "12px", color: "var(--muted)" }}>
                            当前使用
                        </div>
                        <div style={{ 
                            fontSize: "14px", 
                            fontWeight: 600, 
                            color: "var(--teal)",
                            fontFamily: "ui-monospace, SFMono-Regular, monospace"
                        }}>
                            {getCurrentModel(activeTab)}
                        </div>
                    </div>
                </div>

                {/* Model list */}
                <div style={{
                    display: "grid",
                    gap: "8px",
                    overflow: "auto",
                    maxHeight: "45vh",
                    paddingRight: "4px"
                }}>
                    {getModels(activeTab).map(model => {
                        const isCurrent = getCurrentModel(activeTab) === model.id;
                        const isSwitching = switching === activeTab;
                        
                        return (
                            <div
                                key={model.id}
                                onClick={() => !isSwitching && handleSelectModel(activeTab, model.id)}
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "12px",
                                    padding: "12px 14px",
                                    borderRadius: "var(--radius)",
                                    border: isCurrent 
                                        ? "1px solid rgba(217, 139, 43, 0.6)" 
                                        : "1px solid var(--border)",
                                    background: isCurrent 
                                        ? "rgba(217, 139, 43, 0.08)" 
                                        : "rgba(255, 255, 255, 0.7)",
                                    cursor: isSwitching ? "not-allowed" : "pointer",
                                    transition: "all 0.2s ease",
                                    opacity: isSwitching ? 0.6 : 1,
                                    boxShadow: isCurrent 
                                        ? "0 0 0 1px rgba(217, 139, 43, 0.2), 0 4px 12px rgba(217, 139, 43, 0.1)" 
                                        : "none"
                                }}
                            >
                                {/* Radio indicator */}
                                <div style={{
                                    width: "18px",
                                    height: "18px",
                                    borderRadius: "50%",
                                    border: isCurrent 
                                        ? "4px solid var(--accent)" 
                                        : "2px solid var(--border)",
                                    background: "#fff",
                                    flexShrink: 0,
                                    transition: "all 0.2s ease"
                                }}/>
                                
                                <div style={{ flex: 1, minWidth: 0 }}>
                                    <div style={{
                                        fontSize: "14px",
                                        fontWeight: 600,
                                        color: "var(--ink)",
                                        marginBottom: "2px",
                                        overflow: "hidden",
                                        textOverflow: "ellipsis",
                                        whiteSpace: "nowrap"
                                    }}>
                                        {model.name}
                                    </div>
                                    <div style={{
                                        fontSize: "12px",
                                        color: "var(--muted)",
                                        overflow: "hidden",
                                        textOverflow: "ellipsis",
                                        whiteSpace: "nowrap"
                                    }}>
                                        {model.desc}
                                    </div>
                                </div>

                                {isCurrent && (
                                    <span style={{
                                        padding: "4px 10px",
                                        background: "linear-gradient(135deg, #d98b2b 0%, #b66b17 100%)",
                                        color: "#fff8f0",
                                        fontSize: "11px",
                                        fontWeight: 600,
                                        borderRadius: "999px",
                                        flexShrink: 0
                                    }}>
                                        使用中
                                    </span>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Footer */}
                <div style={{
                    display: "flex",
                    justifyContent: "flex-end",
                    gap: "10px",
                    paddingTop: "10px",
                    borderTop: "1px dashed var(--border)"
                }}>
                    <button onClick={onClose} className="btn btn-outline">
                        关闭
                    </button>
                </div>
            </div>
        </div>
    );
}
