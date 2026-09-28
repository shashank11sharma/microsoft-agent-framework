# ============================================================
# 19 - Production Deployment (FastAPI + Streaming)
# ============================================================


# --- SECTION 1: IMPORTS ---
import json
import os
from typing import Annotated

import uvicorn
from agent_framework import Agent, ResponseStream
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# --- SECTION 2: CONFIGURATION ---
# OpenAIChatClient() reads OPENAI_API_KEY, OPENAI_MODEL, and optional OPENAI_BASE_URL from env.
load_dotenv()
client = OpenAIChatClient()
PORT = int(os.getenv("PORT", 8001))


# --- SECTION 3: TOOLS ---
def search_sharepoint_documents(query: Annotated[str, "Document title or keyword to find in SharePoint"]) -> str:
    """Returns matching mock SharePoint document metadata; no tenant is queried."""
    mock = {
        "retention": "Retention Guide | Policy Hub | Owner: Records Team | Status: Approved",
        "atlas": "Project Atlas Plan | Projects | Owner: Atlas PMO | Status: In Review",
        "brand": "Brand Assets | Communications | Owner: Marketing | Status: Approved",
    }
    return next((value for key, value in mock.items() if key in query.lower()), "No matching demo document found")


def get_teams_channel_messages(channel: Annotated[str, "Teams channel name, e.g. 'Content-Governance'"]) -> str:
    """Returns mock Teams messages; no tenant is queried."""
    messages = {
        "content-governance": "Review the retention guide in Policy Hub before Friday.",
        "project-atlas": "The project plan is ready for content-owner review.",
    }
    return messages.get(channel.lower(), "No demo messages found")


def get_outlook_calendar_events(topic: Annotated[str, "Content review topic, e.g. 'Retention Guide'"]) -> str:
    """Returns mock Outlook calendar availability; no tenant is queried."""
    return f"{topic}: SharePoint review meeting on 2026-10-01 at 10:00"


# --- SECTION 4: AGENT ---
agent = Agent(
    client=client,
    name="M365ContentProductionAgent",
    instructions=(
        "You are a content-management assistant with mock SharePoint, Teams, and Outlook tools. "
        "Use the tools for document lookup, channel messages, and review-calendar questions. "
        "The tools do not connect to a real Microsoft 365 tenant."
    ),
    tools=[search_sharepoint_documents, get_teams_channel_messages, get_outlook_calendar_events],
)


# --- SECTION 5: REQUEST SCHEMA ---
class ChatRequest(BaseModel):
    message: str


# --- SECTION 6: API ENDPOINTS ---
app = FastAPI(title="Microsoft 365 Content Assistant API")


@app.get("/health")
async def health() -> dict:
    """GET /health — liveness check."""
    return {"status": "ok", "agent": agent.name}


@app.post("/chat")
async def chat(req: ChatRequest) -> dict:
    """POST /chat — single-turn, returns full response as JSON."""
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="message field is required")

    response = await agent.run(message)
    return {"reply": response.text}


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    """POST /chat/stream — streams tokens as server-sent events (SSE).

    Each event is a JSON line:  {"token": "..."} or {"done": true}
    Clients can consume this with EventSource or fetch + ReadableStream.
    """
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="message field is required")

    async def event_generator():
        stream: ResponseStream = agent.run(message, stream=True)
        async for update in stream:
            if update.text:
                data = json.dumps({"token": update.text})
                yield f"data: {data}\n\n"
        yield "data: " + json.dumps({"done": True}) + "\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering for SSE
        },
    )


# --- SECTION 7: RUN ---
# Start the server:  python 19_production_deployment.py
# Interactive docs:  http://localhost:8001/docs
#
# Test non-streaming:  curl -X POST http://localhost:8001/chat \
#                       -H "Content-Type: application/json" \
#                       -d '{"message": "Find the approved retention guide in SharePoint."}'
#
# Test streaming:      curl -X POST http://localhost:8001/chat/stream \
#                       -H "Content-Type: application/json" \
#                       -d '{"message": "Summarize the content review messages in Teams Content-Governance."}' \
#                       --no-buffer
if __name__ == "__main__":
    print(f"🚀 Agent API running at http://localhost:{PORT}")
    print("   GET  /health")
    print("   POST /chat         — full JSON response")
    print("   POST /chat/stream  — server-sent events")
    print(f"   Docs:  http://localhost:{PORT}/docs")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
