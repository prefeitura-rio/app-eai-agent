from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from src.services.langgraph_servervice.service import run_enhanced_chatbot
import asyncio

router = APIRouter(prefix="/api/v1/langgraph", tags=["langgraph"])


class LangGraphChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str
    agent_config: Optional[Dict[str, Any]] = None


class LangGraphChatResponse(BaseModel):
    response: str
    user_id: str
    session_id: str
    memory_stats: Dict[str, Any]
    error: Optional[str] = None


@router.post("/chat", response_model=LangGraphChatResponse)
async def chat_with_memory(request: LangGraphChatRequest):
    """Chat with LangGraph agent using memory capabilities"""
    try:
        result = await run_enhanced_chatbot(
            user_id=request.user_id,
            session_id=request.session_id,
            message=request.message,
            agent_config=request.agent_config
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return LangGraphChatResponse(
            response=result.get("response", ""),
            user_id=result.get("user_id", request.user_id),
            session_id=result.get("session_id", request.session_id),
            memory_stats=result.get("memory_stats", {})
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "langgraph-chat"} 