# ============================================================
# 16 - Single Agent State Persistence
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio

from agent_framework import Agent, FileHistoryProvider
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()

HISTORY_PATH = ".agent_history"  # single-agent conversation persistence


# --- SECTION 3: SESSION PERSISTENCE WITH FileHistoryProvider ---
# FileHistoryProvider writes every message to disk.
# On the next run, the agent picks up exactly where it left off —
# process restart does NOT wipe the conversation.
persistent_agent = Agent(
    client=client,
    name="PersistentContentAssistant",
    instructions=(
        "You are a content-migration assistant. Remember the SharePoint library, migration project, "
        "and publishing decisions the user shares across sessions."
    ),
    context_providers=[FileHistoryProvider(HISTORY_PATH)],
)


# --- SECTION 4: DEMO HELPERS ---
async def demo_session_persistence():
    print("=" * 60)
    print("💾 SESSION PERSISTENCE — FileHistoryProvider")
    print("   (Run this script twice to see memory survive restarts)")
    print("=" * 60)

    turns = [
        "We are organizing the Policy Hub SharePoint library for the records migration. Remember that the content owner is the Records Team.",
        "Which SharePoint library are we organizing, and who owns the content?",
    ]

    session = persistent_agent.create_session(session_id="persistence")
    for msg in turns:
        print(f"\n💬 Content team: {msg}")
        response = await persistent_agent.run(msg, session=session)
        print(f"🤖 Agent: {response.text}")


# --- SECTION 5: RUN & TEST ---
async def main():
    await demo_session_persistence()


asyncio.run(main())
