"""
Bilibili RAG 知识库系统

核心配置模块 - 支持模型自动轮换
"""
from pydantic_settings import BaseSettings
from pydantic import Field, AliasChoices
from typing import Optional, List
import os
import random


# ============ 阿里云百炼免费模型列表 ============

# LLM 对话模型 (文本生成)
FREE_LLM_MODELS = [
    # Qwen3 系列 (免费额度充足)
    {"id": "qwen3-max", "name": "qwen3-max", "desc": "Qwen3 最强模型，免费100万Token"},
    {"id": "qwen3-max-2026-01-23", "name": "qwen3-max-2026-01-23", "desc": "Qwen3 快照版"},
    {"id": "qwen3-max-2025-09-23", "name": "qwen3-max-2025-09-23", "desc": "Qwen3 快照版"},
    {"id": "qwen3-max-preview", "name": "qwen3-max-preview", "desc": "Qwen3 预览版"},
    
    # Qwen3.5 系列
    {"id": "qwen3.5-plus", "name": "qwen3.5-plus", "desc": "Qwen3.5 Plus，免费100万Token"},
    {"id": "qwen3.5-plus-2026-02-15", "name": "qwen3.5-plus-2026-02-15", "desc": "Qwen3.5 Plus 快照版"},
    {"id": "qwen-plus", "name": "qwen-plus", "desc": "Qwen Plus 免费版"},
    {"id": "qwen-plus-2025-12-01", "name": "qwen-plus-2025-12-01", "desc": "Qwen Plus 快照版"},
    {"id": "qwen-plus-2025-09-11", "name": "qwen-plus-2025-09-11", "desc": "Qwen Plus 快照版"},
    {"id": "qwen-plus-2025-07-28", "name": "qwen-plus-2025-07-28", "desc": "Qwen Plus 快照版"},
    {"id": "qwen-plus-2025-07-14", "name": "qwen-plus-2025-07-14", "desc": "Qwen Plus 快照版"},
    {"id": "qwen-plus-2025-01-25", "name": "qwen-plus-2025-01-25", "desc": "Qwen Plus 快照版"},
    
    # Qwen3 Flash 系列 (免费额度充足)
    {"id": "qwen3-flash", "name": "qwen3-flash", "desc": "Qwen3 Flash 免费100万Token"},
    {"id": "qwen3-flash-2025-09-23", "name": "qwen3-flash-2025-09-23", "desc": "Qwen3 Flash 快照版"},
    {"id": "qwen-flash", "name": "qwen-flash", "desc": "Qwen Flash 免费版"},
    {"id": "qwen-flash-2025-06-12", "name": "qwen-flash-2025-06-12", "desc": "Qwen Flash 快照版"},
    {"id": "qwen-flash-2025-01-25", "name": "qwen-flash-2025-01-25", "desc": "Qwen Flash 快照版"},
    
    # Qwen Coder 系列
    {"id": "qwen3-coder-32b", "name": "qwen3-coder-32b", "desc": "Qwen3 Coder 32B"},
    {"id": "qwen3-coder-32b-instruct", "name": "qwen3-coder-32b-instruct", "desc": "Qwen3 Coder 32B Instruct"},
    {"id": "qwen2.5-coder-32b-instruct", "name": "qwen2.5-coder-32b-instruct", "desc": "Qwen2.5 Coder"},
    
    # Qwen 旧版
    {"id": "qwen-max", "name": "qwen-max", "desc": "Qwen Max 免费100万Token"},
    {"id": "qwen-max-latest", "name": "qwen-max-latest", "desc": "Qwen Max 最新版"},
    {"id": "qwen-max-2025-01-25", "name": "qwen-max-2025-01-25", "desc": "Qwen Max 快照版"},
    {"id": "qwen-max-2024-09-19", "name": "qwen-max-2024-09-19", "desc": "Qwen Max 快照版"},
    {"id": "qwen-max-2024-04-28", "name": "qwen-max-2024-04-28", "desc": "Qwen Max 快照版"},
    
    # Qwen Long (长文本)
    {"id": "qwen-long", "name": "qwen-long", "desc": "Qwen 长文本模型，免费额度充足"},
]

# 向量 Embedding 模型
FREE_EMBEDDING_MODELS = [
    {"id": "text-embedding-v3", "name": "text-embedding-v3", "desc": "文本向量 v3"},
    {"id": "text-embedding-v2", "name": "text-embedding-v2", "desc": "文本向量 v2"},
    {"id": "text-embedding-3-small", "name": "text-embedding-3-small", "desc": "文本向量 3 Small"},
    
    # Qwen3 Embedding 系列
    {"id": "qwen3-embedding-0.6b", "name": "qwen3-embedding-0.6b", "desc": "Qwen3 Embedding 0.6B"},
    {"id": "qwen3-embedding-4b", "name": "qwen3-embedding-4b", "desc": "Qwen3 Embedding 4B"},
    {"id": "qwen3-embedding-8b", "name": "qwen3-embedding-8b", "desc": "Qwen3 Embedding 8B"},
    
    # Qwen3 Reranker 系列
    {"id": "qwen3-reranker-0.6b", "name": "qwen3-reranker-0.6b", "desc": "Qwen3 Reranker 0.6B"},
    {"id": "qwen3-reranker-4b", "name": "qwen3-reranker-4b", "desc": "Qwen3 Reranker 4B"},
    {"id": "qwen3-reranker-8b", "name": "qwen3-reranker-8b", "desc": "Qwen3 Reranker 8B"},
]

# 语音 ASR/TTS 模型
FREE_ASR_MODELS = [
    # Qwen3 ASR 系列
    {"id": "qwen3-asr-flash", "name": "qwen3-asr-flash", "desc": "Qwen3 ASR Flash"},
    {"id": "qwen3-asr-flash-realtime", "name": "qwen3-asr-flash-realtime", "desc": "Qwen3 ASR Flash 实时"},
    {"id": "qwen3-asr-flash-realtime-2026-02-10", "name": "qwen3-asr-flash-realtime-2026-02-10", "desc": "Qwen3 ASR Flash 实时 (2026-02-10)"},
    {"id": "qwen3-asr-flash-filetrans", "name": "qwen3-asr-flash-filetrans", "desc": "Qwen3 ASR Flash 文件转写"},
    
    # Qwen3 TTS 系列
    {"id": "qwen3-tts-flash", "name": "qwen3-tts-flash", "desc": "Qwen3 TTS Flash"},
    {"id": "qwen3-tts-flash-realtime", "name": "qwen3-tts-flash-realtime", "desc": "Qwen3 TTS Flash 实时"},
    {"id": "qwen3-tts-vd-realtime-2025-12-16", "name": "qwen3-tts-vd-realtime-2025-12-16", "desc": "Qwen3 TTS VD 实时 (2025-12-16)"},
    {"id": "qwen3-tts-vd-realtime-2026-01-15", "name": "qwen3-tts-vd-realtime-2026-01-15", "desc": "Qwen3 TTS VD 实时 (2026-01-15)"},
    {"id": "qwen3-tts-instruct-flash", "name": "qwen3-tts-instruct-flash", "desc": "Qwen3 TTS Instruct Flash"},
    {"id": "qwen3-tts-instruct-flash-realtime", "name": "qwen3-tts-instruct-flash-realtime", "desc": "Qwen3 TTS Instruct Flash 实时"},
    {"id": "qwen3-tts-instruct-flash-realtime-2026-01", "name": "qwen3-tts-instruct-flash-realtime-2026-01", "desc": "Qwen3 TTS Instruct Flash 实时 (2026-01)"},
    
    # Qwen 语音交互
    {"id": "qwen-voice-enrollment", "name": "qwen-voice-enrollment", "desc": "Qwen 语音注册"},
    {"id": "qwen-voice-design", "name": "qwen-voice-design", "desc": "Qwen 语音设计"},
    
    # Qwen3 实时翻译
    {"id": "qwen3-livetranslate-flash-realtime", "name": "qwen3-livetranslate-flash-realtime", "desc": "Qwen3 实时翻译"},
    {"id": "qwen3-livetranslate-flash-realtime-2025-09", "name": "qwen3-livetranslate-flash-realtime-2025-09", "desc": "Qwen3 实时翻译 (2025-09)"},
    
    # Paraformer 系列
    {"id": "paraformer-v2", "name": "paraformer-v2", "desc": "Paraformer v2"},
    {"id": "paraformer-realtime-v2", "name": "paraformer-realtime-v2", "desc": "Paraformer 实时 v2"},
    {"id": "paraformer-v1", "name": "paraformer-v1", "desc": "Paraformer v1"},
    
    # SenseVoice
    {"id": "sensevoice-5", "name": "sensevoice-5", "desc": "SenseVoice 5"},
    {"id": "sensevoice-5-onnx", "name": "sensevoice-5-onnx", "desc": "SenseVoice 5 ONNX"},
    {"id": "sensevoice-large-onnx", "name": "sensevoice-large-onnx", "desc": "SenseVoice Large ONNX"},
    
    # Fun-ASR
    {"id": "fun-asr-diarization", "name": "fun-asr-diarization", "desc": "Fun-ASR 话者分离"},
    {"id": "fun-asr-diarization-onnx", "name": "fun-asr-diarization-onnx", "desc": "Fun-ASR 话者分离 ONNX"},
    
    # Gummy
    {"id": "gummy-asr", "name": "gummy-asr", "desc": "Gummy ASR"},
    {"id": "gummy-translate", "name": "gummy-translate", "desc": "Gummy 翻译"},
]

FREE_EMBEDDING_MODELS = [
    {"id": "text-embedding-v3", "name": "text-embedding-v3", "desc": "向量模型，免费"},
    {"id": "text-embedding-2", "name": "text-embedding-2", "desc": "备选向量模型，免费"},
]

FREE_ASR_MODELS = [
    # Paraformer 系列
    {"id": "paraformer-v2", "name": "paraformer-v2", "desc": "ASR转写，免费"},
    {"id": "paraformer-realtime-v2", "name": "paraformer-realtime-v2", "desc": "实时ASR，免费"},
    {"id": "paraformer-v1", "name": "paraformer-v1", "desc": "旧版ASR，免费"},
    # Qwen3 ASR 系列
    {"id": "qwen3-asr-flash", "name": "qwen3-asr-flash", "desc": "Qwen3 ASR Flash"},
    {"id": "qwen3-asr-flash-realtime", "name": "qwen3-asr-flash-realtime", "desc": "Qwen3 ASR Flash 实时"},
    {"id": "qwen3-asr-flash-realtime-2026-02-10", "name": "qwen3-asr-flash-realtime-2026-02-10", "desc": "Qwen3 ASR Flash 实时 (2026-02-10)"},
    {"id": "qwen3-asr-flash-filetrans", "name": "qwen3-asr-flash-filetrans", "desc": "Qwen3 ASR Flash 文件转写"},
    # Qwen3 TTS 系列
    {"id": "qwen3-tts-flash", "name": "qwen3-tts-flash", "desc": "Qwen3 TTS Flash"},
    {"id": "qwen3-tts-flash-realtime", "name": "qwen3-tts-flash-realtime", "desc": "Qwen3 TTS Flash 实时"},
    {"id": "qwen3-tts-vd-realtime-2025-12-16", "name": "qwen3-tts-vd-realtime-2025-12-16", "desc": "Qwen3 TTS VD 实时 (2025-12-16)"},
    {"id": "qwen3-tts-vd-realtime-2026-01-15", "name": "qwen3-tts-vd-realtime-2026-01-15", "desc": "Qwen3 TTS VD 实时 (2026-01-15)"},
    {"id": "qwen3-tts-instruct-flash", "name": "qwen3-tts-instruct-flash", "desc": "Qwen3 TTS Instruct Flash"},
    {"id": "qwen3-tts-instruct-flash-realtime", "name": "qwen3-tts-instruct-flash-realtime", "desc": "Qwen3 TTS Instruct Flash 实时"},
    {"id": "qwen3-tts-instruct-flash-realtime-2026-01", "name": "qwen3-tts-instruct-flash-realtime-2026-01", "desc": "Qwen3 TTS Instruct Flash 实时 (2026-01)"},
    # Qwen3 语音交互
    {"id": "qwen-voice-enrollment", "name": "qwen-voice-enrollment", "desc": "Qwen 语音注册"},
    {"id": "qwen-voice-design", "name": "qwen-voice-design", "desc": "Qwen 语音设计"},
    # Qwen3 实时翻译
    {"id": "qwen3-livetranslate-flash-realtime", "name": "qwen3-livetranslate-flash-realtime", "desc": "Qwen3 实时翻译"},
    {"id": "qwen3-livetranslate-flash-realtime-2025-09", "name": "qwen3-livetranslate-flash-realtime-2025-09", "desc": "Qwen3 实时翻译 (2025-09)"},
]

# 当前选中的模型（内存中）
_current_llm_model = None
_current_embedding_model = None
_current_asr_model = None


def get_free_model(model_type: str, prefer_specific: str = None) -> str:
    """
    获取可用的免费模型
    
    Args:
        model_type: 模型类型 ('llm', 'embedding', 'asr')
        prefer_specific: 偏好的具体模型
    
    Returns:
        可用的模型名称
    """
    global _current_llm_model, _current_embedding_model, _current_asr_model
    
    if model_type == "llm":
        models = FREE_LLM_MODELS
        current = _current_llm_model
    elif model_type == "embedding":
        models = FREE_EMBEDDING_MODELS
        current = _current_embedding_model
    elif model_type == "asr":
        models = FREE_ASR_MODELS
        current = _current_asr_model
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # 如果指定了具体模型且在列表中，优先使用
    if prefer_specific:
        for m in models:
            if m["id"] == prefer_specific:
                return prefer_specific
    
    # 如果当前已有选中的模型，使用它
    if current:
        return current
    
    # 否则随机选择一个
    return random.choice(models)["id"]


def set_model(model_type: str, model_id: str) -> bool:
    """
    设置当前使用的模型
    
    Args:
        model_type: 模型类型 ('llm', 'embedding', 'asr')
        model_id: 模型 ID
    
    Returns:
        是否设置成功
    """
    global _current_llm_model, _current_embedding_model, _current_asr_model
    
    if model_type == "llm":
        for m in FREE_LLM_MODELS:
            if m["id"] == model_id:
                _current_llm_model = model_id
                return True
    elif model_type == "embedding":
        for m in FREE_EMBEDDING_MODELS:
            if m["id"] == model_id:
                _current_embedding_model = model_id
                return True
    elif model_type == "asr":
        for m in FREE_ASR_MODELS:
            if m["id"] == model_id:
                _current_asr_model = model_id
                return True
    
    return False


def get_current_model(model_type: str) -> str:
    """获取当前选中的模型"""
    global _current_llm_model, _current_embedding_model, _current_asr_model
    
    if model_type == "llm":
        return _current_llm_model or get_free_model("llm")
    elif model_type == "embedding":
        return _current_embedding_model or get_free_model("embedding")
    elif model_type == "asr":
        return _current_asr_model or get_free_model("asr")
    return None


class Settings(BaseSettings):
    """应用配置"""
    
    # OpenAI / LLM 配置
    openai_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("DASHSCOPE_API_KEY", "OPENAI_API_KEY"),
    )
    openai_base_url: str = Field(default="https://api.openai.com/v1", env="OPENAI_BASE_URL")
    llm_model: str = Field(default="gpt-4-turbo", env="LLM_MODEL")
    embedding_model: str = Field(default="text-embedding-3-small", env="EMBEDDING_MODEL")

    # DashScope ASR
    dashscope_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/api/v1",
        env="DASHSCOPE_BASE_URL"
    )
    asr_model: str = Field(default="paraformer-v2", env="ASR_MODEL")
    asr_timeout: int = Field(default=600, env="ASR_TIMEOUT")
    asr_model_local: str = Field(default="paraformer-realtime-v2", env="ASR_MODEL_LOCAL")
    asr_input_format: str = Field(default="pcm", env="ASR_INPUT_FORMAT")
    
    # 应用配置
    app_host: str = Field(default="0.0.0.0", env="APP_HOST")
    app_port: int = Field(default=8000, env="APP_PORT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # 数据库
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/bilibili_rag.db",
        env="DATABASE_URL"
    )
    
    # ChromaDB
    chroma_persist_directory: str = Field(
        default="./data/chroma_db",
        env="CHROMA_PERSIST_DIRECTORY"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# 全局配置实例
settings = Settings()


def ensure_directories():
    """确保必要的目录存在"""
    dirs = [
        "data",
        settings.chroma_persist_directory,
        "logs"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
