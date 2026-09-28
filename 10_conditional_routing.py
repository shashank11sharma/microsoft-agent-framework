# ============================================================
# 10 - Conditional Routing & Handoffs
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()

# --- SECTION 3: SPECIALIST + ROUTER AGENTS ---
sharepoint_agent = Agent(
    client=client,
    name="SharePointLibraryAgent",
    instructions=(
        "You are a SharePoint library specialist. Handle ONLY document discovery, metadata, permissions, and version questions. "
        "Be precise and professional."
    ),
)
teams_agent = Agent(
    client=client,
    name="TeamsAgent",
    instructions=(
        "You are a Teams collaboration specialist. Handle ONLY channel, message, and content-review coordination questions. "
        "Ask for the team or channel name when relevant."
    ),
)
outlook_calendar_agent = Agent(
    client=client,
    name="OutlookCalendarAgent",
    instructions=(
        "You are an Outlook calendar specialist. Handle ONLY review meetings, publishing schedules, and reminders. "
        "Be clear about dates and times."
    ),
)
content_governance_agent = Agent(
    client=client,
    name="ContentGovernanceAgent",
    instructions="You are a content-governance specialist. Handle cross-service ownership, retention, and publishing questions.",
)
router_agent = Agent(
    client=client,
    name="RouterAgent",
    instructions=(
        "You are a Microsoft 365 content request classifier. "
        "Read the user message and respond with EXACTLY ONE WORD: "
        "SHAREPOINT, TEAMS, OUTLOOK, or GENERAL. No other text."
    ),
)

ROUTE_MAP = {
    "SHAREPOINT": sharepoint_agent,
    "TEAMS": teams_agent,
    "OUTLOOK": outlook_calendar_agent,
    "GENERAL": content_governance_agent,
}


# --- SECTION 4: ROUTING LOGIC ---
async def handle_query(query: str) -> str:
    # Run the router agent to know which agent to call
    router_response = await router_agent.run(query)
    category = router_response.messages[-1].text.strip().upper()

    # Check the given agent is available in ROUTE_MAP
    category = category if category in ROUTE_MAP else "GENERAL"
    specialist = ROUTE_MAP[category]
    print(f"  📍 Routed to: {specialist.name}")

    # Call the agent provided by route agent
    specialist_response = await specialist.run(query)
    return specialist_response.messages[-1].text


# --- SECTION 5: RUN & TEST ---
async def main():
    queries = [
        "Find the latest approved retention policy in SharePoint and tell me its owner.",
        "How do I organize a Teams channel for reviewing document changes?",
        "Schedule an Outlook meeting next week to approve the new publishing guide.",
        "Who should own cross-team content retention standards?",
    ]
    for q in queries:
        print(f"\n💬 Shashank: {q}")
        response = await handle_query(q)
        print(f"🤖 Response: {response}")
        print("=" * 60)


asyncio.run(main())
