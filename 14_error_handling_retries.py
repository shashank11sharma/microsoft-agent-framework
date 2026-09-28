# ============================================================
# 14 - Error Handling & Retries
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import Annotated

from agent_framework import (
    Agent,
    AgentContext,
    AgentMiddleware,
    FunctionInvocationContext,
    FunctionMiddleware,
    MiddlewareTermination,
)
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()


# --- SECTION 3: RETRY MIDDLEWARE ---
# Retries the entire agent call when it fails (network glitch, rate-limit, etc.)
class RetryMiddleware(AgentMiddleware):
    def __init__(self, max_retries: int = 3, delay_seconds: float = 1.0):
        self.max_retries = max_retries
        self.delay_seconds = delay_seconds

    async def process(
        self,
        context: AgentContext,
        call_next: Callable[[], Awaitable[None]],
    ):
        for attempt in range(1, self.max_retries + 1):
            try:
                await call_next()
                return  # success — stop retrying
            except Exception as e:
                if attempt == self.max_retries:
                    print(f"  RetryMiddleware ❌ All {self.max_retries} retries exhausted. Last error: {e}")
                    raise
                print(f"  ⚠️  Attempt {attempt} failed ({e}). Retrying in {self.delay_seconds}s...")
                await asyncio.sleep(self.delay_seconds)


# --- SECTION 4: TOOL-LEVEL ERROR MIDDLEWARE ---
# Catches tool/function failures and returns a safe fallback string
# so the agent can continue instead of crashing the whole run.
class SafeToolMiddleware(FunctionMiddleware):
    def __init__(self, max_retries: int = 3, delay_seconds: float = 0.5):
        self.max_retries = max_retries
        self.delay_seconds = delay_seconds

    async def process(
        self,
        context: FunctionInvocationContext,
        call_next: Callable[[], Awaitable[None]],
    ):
        for attempt in range(1, self.max_retries + 1):
            try:
                await call_next()
                return
            except Exception as e:
                tool_name = context.function.name
                if attempt == self.max_retries:
                    context.result = f"[Tool '{tool_name}' failed: {e}. Please try a different approach.]"
                    print(
                        f"  SafeToolMiddleware ❌ All {self.max_retries} retries exhausted for {tool_name}."
                        f" Last error: {e}"
                    )
                    raise MiddlewareTermination()  # stop the middleware chain with our fallback

                print(f"  ⚠️  Attempt {attempt} failed ({e}). Retrying in {self.delay_seconds}s...")
                await asyncio.sleep(self.delay_seconds)


# --- SECTION 5: FLAKY TOOLS (simulate real-world unreliability) ---
_call_counts: dict[str, int] = {}


def flaky_sharepoint_lookup(document_id: Annotated[str, "SharePoint document ID, e.g. 'POL-104'"]) -> str:
    """Looks up mock SharePoint document metadata and may fail on the first attempt."""
    _call_counts[document_id] = _call_counts.get(document_id, 0) + 1
    if _call_counts[document_id] < 2:
        raise ConnectionError(f"Timeout searching for SharePoint document {document_id}")
    documents = {"POL-104": "Retention Guide | Policy Hub | Owner: Records Team", "ATLAS-22": "Project Plan | Projects | Owner: Atlas PMO"}
    return documents.get(document_id.upper(), f"Document {document_id} not found")


def unreliable_calendar_lookup(meeting: Annotated[str, "Outlook meeting name, e.g. 'Policy Review'"]) -> str:
    """Looks up mock Outlook calendar availability and randomly fails."""
    if random.random() < 0.8:  # 80% of time fail
        raise RuntimeError("Outlook calendar service temporarily unavailable")
    return f"{meeting}: review slot available on 2026-10-01 at 10:00"


# --- SECTION 6: AGENT WITH BOTH MIDDLEWARE LAYERS ---
resilient_agent = Agent(
    client=client,
    name="ResilientAgent",
    instructions=(
        "You are a Microsoft 365 content assistant. Use your tools to look up SharePoint documents and "
        "Outlook review availability. If a tool fails, explain what happened and retry or suggest alternatives."
    ),
    tools=[flaky_sharepoint_lookup, unreliable_calendar_lookup],
    middleware=[
        RetryMiddleware(max_retries=3, delay_seconds=0.5),
        SafeToolMiddleware(max_retries=3, delay_seconds=0.5),
    ],
)


# --- SECTION 7: RUN & TEST ---
async def main():
    queries = [
        "Find SharePoint document POL-104 and tell me its owner.",
        "Check Outlook availability for the Policy Review meeting.",
        "Find SharePoint document ATLAS-22 and check the Outlook slot for the Project Atlas review.",
    ]

    for query in queries:
        print(f"\n💬 {query}")
        try:
            response = await resilient_agent.run(query)
            print(f"🤖 {response.text}")
        except Exception as e:
            print(f"💥 Unrecoverable error: {e}")
        print("-" * 55)


asyncio.run(main())
