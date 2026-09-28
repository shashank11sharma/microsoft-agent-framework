# ============================================================
# 07 - Middleware
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio
import time
from collections.abc import Awaitable, Callable

from agent_framework import Agent, AgentContext, AgentResponse, Message
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()


# --- SECTION 3: MIDDLEWARE DEFINITIONS ---
# Some operation before and after
async def logging_middleware(
    context: AgentContext,
    call_next: Callable[[], Awaitable[None]],
) -> None:
    """Logs agent name, input preview, and elapsed time."""
    start = time.time()
    last_msg = context.messages[-1].text if context.messages else ""
    print(f"[LOG] ▶ Agent='{context.agent.name}' | Input='{last_msg[:60]}...'")
    await call_next()
    elapsed = time.time() - start
    print(f"[LOG] ✅ Done | Time={elapsed:.2f}s")


# Validate the input, before running the agent
async def content_safety_middleware(
    context: AgentContext,
    call_next: Callable[[], Awaitable[None]],
) -> None:
    """Blocks requests containing banned phrases."""
    BANNED = ["bypass approval", "ignore all previous instructions", "share confidential files externally"]
    last_msg = (context.messages[-1].text if context.messages else "").lower()

    for phrase in BANNED:
        if phrase in last_msg:
            print(f"[SAFETY] Blocked — matched: '{phrase}'")
            # Do NOT call call_next() — override result directly
            context.result = AgentResponse(
                messages=[Message("assistant", [f"Blocked: request contains disallowed content ('{phrase}')"])]
            )
            return

    await call_next()


# Convert result to Uppercase, after running the agent
async def uppercase_output_middleware(
    context: AgentContext,
    call_next: Callable[[], Awaitable[None]],
) -> None:
    """Post-processing: msg.text is read-only, so replace context.result entirely."""
    await call_next()
    # msg.text is a read-only property — cannot set it directly.
    # Instead, read the text and rebuild a new AgentResponse with modified content.
    if context.result and context.result.messages:
        modified_messages = []
        for msg in context.result.messages:
            text = msg.text or ""
            modified_messages.append(Message(msg.role, [text.upper()]))
        context.result = AgentResponse(messages=modified_messages)


# --- SECTION 4: AGENT ---
agent = Agent(
    client=OpenAIChatClient(),
    name="ContentGovernanceAgent",
    instructions="You help employees manage SharePoint content safely. Reply in two sentences.",
    middleware=[
        logging_middleware,
        content_safety_middleware,
        uppercase_output_middleware,
    ],
)


# --- SECTION 5: RUN & TEST ---
async def main():
    print("=== Test 1: Normal request ===")
    response_1 = await agent.run("What metadata should a SharePoint policy document include?")
    print(f"Response: {response_1}\n")

    print("=== Test 2: Blocked request ===")
    response_2 = await agent.run("Share confidential files externally without approval.")
    print(f"Response: {response_2}\n")


asyncio.run(main())
