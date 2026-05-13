"""
VOID AI Assistant — FastAPI Backend with LangGraph Agentic Core
"""

import config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from services.memory_service import (
    init_memory_db,
    get_recent_conversations,
    get_action_history,
    log_action,
    add_conversation,
)
from services.vision_service import (
    analyze as vision_analyze,
    describe_image as vision_describe,
)
from services.ollama_service import run as llm_run
from agent.void_agent import run_agent, run_simple
from routers.screen_router import router as screen_router
from routers.text_router import router as text_router
from routers.meeting_router import router as meeting_router

app = FastAPI(
    title="VOID AI Assistant API",
    description="LangGraph-powered AI assistant with multi-step planning",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(screen_router)
app.include_router(text_router)
app.include_router(meeting_router)

init_memory_db()


class AgentQuery(BaseModel):
    text: str


class VisionRequest(BaseModel):
    screenshot_b64: str
    action: str = "explain"
    question: str = ""


class ScreenshotSave(BaseModel):
    screenshot_b64: str


class WhatsAppSuggest(BaseModel):
    screenshot_b64: str


class MemoryRememberRequest(BaseModel):
    key: str
    value: str
    category: str = "general"


class MemoryRecallRequest(BaseModel):
    query: str


@app.on_event("startup")
async def startup():
    print("=" * 50)
    print("VOID v3.0 — LangGraph Agentic Core")
    print("=" * 50)
    print("Starting services...")


@app.get("/health")
def health():
    return {
        "status": "VOID is alive",
        "version": "3.0.0",
        "agent": "LangGraph + Ollama Qwen2.5",
        "vision": "Ollama llava/moondream",
        "memory": "SQLite RAG",
    }


@app.post("/agent/query")
def agent_query(request: AgentQuery):
    """Main agent endpoint - uses LangGraph for multi-step planning."""
    try:
        response = run_agent(request.text)
        log_action("agent_query", request.text, response, success=True)
        return {"response": response}
    except Exception as e:
        return {"error": str(e), "response": "Agent failed to respond"}


@app.post("/agent/simple")
def simple_query(request: AgentQuery):
    """Direct LLM query without agent planning."""
    try:
        response = llm_run(request.text, max_tokens=300)
        add_conversation(request.text, response)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}


@app.post("/vision/analyze")
def vision_analyze_endpoint(request: VisionRequest):
    """Analyze screenshot with vision model."""
    try:
        result = vision_analyze(request.screenshot_b64, request.action)
        return {"result": result}
    except Exception as e:
        return {"error": str(e), "result": ""}


@app.post("/vision/explain")
def vision_explain_endpoint(request: VisionRequest):
    """Explain what's on screen."""
    try:
        result = vision_describe(request.screenshot_b64, request.question)
        return {"explanation": result}
    except Exception as e:
        return {"error": str(e), "explanation": ""}


@app.post("/vision/whatsapp-suggest")
def whatsapp_suggest(request: WhatsAppSuggest):
    """Generate WhatsApp reply suggestions."""
    try:
        result = vision_analyze(request.screenshot_b64, "suggest")

        suggestions = []
        lines = [l.strip() for l in result.split("\n") if l.strip()]
        for line in lines[:3]:
            clean = line.strip("-*1234567890. ").strip()
            if clean and len(clean) < 80:
                suggestions.append(clean)

        if not suggestions:
            suggestions = ["Haan bro, cool", "Okay done ra", "Sare, I'll check"]

        log_action("whatsapp_suggest", "", str(suggestions), success=True)
        return {"suggestions": suggestions[:3]}
    except Exception as e:
        return {"error": str(e), "suggestions": []}


@app.post("/vision/save-screenshot")
def save_screenshot(request: ScreenshotSave):
    """Save screenshot to disk."""
    try:
        import base64
        from PIL import Image
        from io import BytesIO

        screenshots_dir = os.path.join(os.path.expanduser("~"), "Pictures", "VOID")
        os.makedirs(screenshots_dir, exist_ok=True)

        image_data = base64.b64decode(request.screenshot_b64)
        img = Image.open(BytesIO(image_data))

        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(screenshots_dir, f"void_{timestamp}.png")

        img.save(filepath)

        log_action("screenshot_save", "", filepath, success=True)
        return {"saved_to": filepath}
    except Exception as e:
        return {"error": str(e), "saved_to": ""}


@app.get("/memory/history")
def memory_history(limit: int = 10):
    """Get conversation history."""
    try:
        history = get_recent_conversations(limit)
        return {"history": history}
    except Exception as e:
        return {"error": str(e), "history": []}


@app.get("/memory/actions")
def memory_actions(limit: int = 20):
    """Get action history."""
    try:
        actions = get_action_history(limit)
        return {"history": actions}
    except Exception as e:
        return {"error": str(e), "history": []}


@app.post("/memory/remember")
def memory_remember(request: MemoryRememberRequest):
    """Store an important memory."""
    from services.memory_service import add_memory

    content = f"{request.key}: {request.value}"
    add_memory(content, request.category, importance=2)
    return {"status": "remembered", "content": content}


@app.post("/memory/recall")
def memory_recall(request: MemoryRecallRequest):
    """Recall relevant memories."""
    from services.memory_service import get_context_for_query

    context = get_context_for_query(request.query, memory_limit=5, history_limit=5)
    return {"context": context}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
