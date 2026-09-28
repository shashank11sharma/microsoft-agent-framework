# ============================================================
# 02 - Agent Instructions & System Prompts
# ============================================================

# --- SECTION 1: IMPORTS ---
import asyncio

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()

# One shared client — all agents reuse the same model connection.
client = OpenAIChatClient()

# --- SECTION 3: THREE AGENTS WITH DIFFERENT INSTRUCTIONS ---
tech_writer = Agent(
    client=client,
    name="PolicyWriter",
    instructions=(
        "You are a SharePoint information architect writing document-library guidance. "
        "Use formal English and bullet points for lists. "
        "Never use slang, emojis, or casual language. "
        "End every response with: 'Confirm the current policy in the SharePoint library.'"
    ),
)

onboarding_bot = Agent(
    client=client,
    name="ContentOnboardingBot",
    instructions=(
        "You are a warm, encouraging assistant helping new employees find content in SharePoint, Teams, and Outlook. "
        "Use simple language and short sentences. "
        "Always end with an emoji and a helpful one-line next step."
    ),
)

security_reviewer = Agent(
    client=client,
    name="ContentGovernanceReviewer",
    instructions=(
        "You are a strict SharePoint content-governance reviewer. "
        "Look ONLY for: exposed personal data, oversharing, missing retention metadata, "
        "and unsafe external sharing. Ignore style issues entirely. "
        "If no issues are found, respond: 'No content-governance issues detected.'"
    ),
)

# --- SECTION 4: RUN & TEST ---
TOPIC = "How should our team organize and govern project documents in SharePoint?"

CODE = """
Document: Employee-Records-Final-v3.docx
Library: General Documents
Sharing: Anyone with the link
Retention label: None
Contains: employee names, home addresses, and personal phone numbers
"""


async def main():
    print("=" * 60)
    print("SAME CONTENT REQUEST — 3 DIFFERENT SYSTEM PROMPTS")
    print("=" * 60)

    response_1 = await tech_writer.run(TOPIC)
    print(f"\n📝 PolicyWriter:\n{response_1}")
    print("=" * 60)

    response_2 = await onboarding_bot.run(TOPIC)
    print(f"\n👋 ContentOnboardingBot:\n{response_2}")
    print("=" * 60)

    response_3 = await security_reviewer.run(f"Review this SharePoint item:\n{CODE}")
    print(f"\n🔐 ContentGovernanceReviewer:\n{response_3}")
    print("=" * 60)


asyncio.run(main())
