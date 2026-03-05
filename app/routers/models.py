"""
模型管理 API
"""
from fastapi import APIRouter
from typing import Dict, List
from pydantic import BaseModel

from app.config import (
    FREE_LLM_MODELS,
    FREE_EMBEDDING_MODELS,
    FREE_ASR_MODELS,
    set_model,
    get_current_model,
)

router = APIRouter(prefix="/api/models", tags=["models"])


class ModelInfo(BaseModel):
    id: str
    name: str
    desc: str


class ModelListResponse(BaseModel):
    llm_models: List[ModelInfo]
    embedding_models: List[ModelInfo]
    asr_models: List[ModelInfo]
    current_llm: str
    current_embedding: str
    current_asr: str


class SetModelRequest(BaseModel):
    model_type: str  # 'llm', 'embedding', 'asr'
    model_id: str


@router.get("", response_model=ModelListResponse)
async def get_models():
    """获取所有可用模型列表"""
    return {
        "llm_models": [ModelInfo(**m) for m in FREE_LLM_MODELS],
        "embedding_models": [ModelInfo(**m) for m in FREE_EMBEDDING_MODELS],
        "asr_models": [ModelInfo(**m) for m in FREE_ASR_MODELS],
        "current_llm": get_current_model("llm"),
        "current_embedding": get_current_model("embedding"),
        "current_asr": get_current_model("asr"),
    }


@router.post("/set")
async def set_current_model(request: SetModelRequest):
    """设置当前使用的模型"""
    success = set_model(request.model_type, request.model_id)
    if success:
        return {
            "success": True,
            "message": f"已切换到 {request.model_id}",
            "current": {
                "llm": get_current_model("llm"),
                "embedding": get_current_model("embedding"),
                "asr": get_current_model("asr"),
            }
        }
    return {
        "success": False,
        "message": f"设置失败：无效的模型 {request.model_id}"
    }