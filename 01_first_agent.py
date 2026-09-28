# ============================================================
# 01 - Setup & Installation
# ============================================================

# --- SECTION 1: IMPORTS ---
import asyncio
import os

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
missing_settings = [
    name for name in ("OPENAI_API_KEY", "OPENAI_MODEL") if not os.getenv(name)
]
if missing_settings:
    raise RuntimeError(
        f"Missing {', '.join(missing_settings)}. Copy .env.example to .env and "
        "set the API key and model deployment name. For Microsoft Foundry, "
        "also configure OPENAI_BASE_URL in .env."
    )


# --- SECTION 3: AGENT DEFINITION ---
# OpenAIChatClient() reads OPENAI_API_KEY, OPENAI_MODEL, and optional OPENAI_BASE_URL.
agent = Agent(
    client=OpenAIChatClient(),
    name="ContentLibraryAssistant",
    instructions="You help employees find and manage SharePoint content. Reply in exactly one sentence.",
)


# --- SECTION 4: RUN & TEST ---
async def main():
    result = await agent.run(
        "Draft a one-sentence announcement that the new document-retention guide is available in SharePoint."
    )
    print(f"\n🤖 Agent: {result}")


asyncio.run(main())
