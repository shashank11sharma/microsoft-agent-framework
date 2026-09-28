# ============================================================
# 04 Tools & Function Calling
# ============================================================

# --- SECTION 1: IMPORTS ---
import asyncio
import datetime
import json
from typing import Annotated

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()

# --- SECTION 3: TOOL DEFINITIONS ---
# Docstring = tool description (shown to the model).
# Annotated[type, "..."] = parameter description (shown to the model).


def get_outlook_calendar_events() -> str:
    """Returns mock Outlook calendar events for a content review."""
    return json.dumps(
        [
            {"subject": "SharePoint policy review", "date": "2026-10-01", "time": "10:00"},
            {"subject": "Teams publishing check-in", "date": "2026-10-02", "time": "14:30"},
        ]
    )


def calculate(expression: Annotated[str, "A math expression, e.g. '2 + 2' or '(10 ** 3) / 4'"]) -> str:
    """Evaluates a safe mathematical expression and returns the numeric result."""
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error: {e}"


def search_sharepoint_documents(query: Annotated[str, "Search phrase for the SharePoint document library"]) -> str:
    """Searches mock SharePoint library data for matching documents."""
    documents = [
        {"name": "Retention-Guide.docx", "library": "Policy Hub", "summary": "Retention labels and review dates"},
        {"name": "Project-Atlas-Plan.docx", "library": "Project Atlas", "summary": "Project plan and publishing milestones"},
    ]
    matches = [item for item in documents if query.lower() in str(item).lower()]
    return json.dumps(matches)


def get_teams_channel_messages(channel: Annotated[str, "Teams channel name, e.g. 'Content-Governance'"]) -> str:
    """Returns mock recent messages from a Teams channel."""
    messages = {
        "content-governance": ["Review the new retention guide before publishing.", "Add an owner to each policy document."],
        "project-atlas": ["The project plan is ready for review."],
    }
    return json.dumps(messages.get(channel.lower(), []))


def save_document_draft(
    filename: Annotated[str, "Local draft filename, e.g. 'retention-guide.txt'"],
    content: Annotated[str, "Draft content for a SharePoint document"],
) -> str:
    """Saves a local draft file; this demo does not publish to SharePoint."""
    try:
        with open(filename, "w") as f:
            f.write(content)
        return f"✅ Saved '{filename}' ({len(content)} chars)"
    except Exception as e:
        return f"❌ Error: {e}"


# --- SECTION 4: AGENT WITH TOOLS ---
agent = Agent(
    client=OpenAIChatClient(),
    name="M365ContentToolAgent",
    instructions=(
        "You are a content-management assistant with mock Microsoft 365 tools. "
        "Use the tools for SharePoint document searches, Teams messages, Outlook calendar events, and saved drafts. "
        "The mock tools do not access a real Microsoft 365 tenant."
    ),
    tools=[
        get_outlook_calendar_events,
        calculate,
        search_sharepoint_documents,
        get_teams_channel_messages,
        save_document_draft,
    ],
)


# --- SECTION 5: RUN & TEST ---
# These are all independent single-turn calls — no thread needed.
async def main():
    prompts = [
        "Show my Outlook calendar events for the content review.",
        "Calculate how many days are in 12 weeks.",
        "Search SharePoint for the retention guide.",
        "Show recent messages in the Content-Governance Teams channel.",
        "Save a draft called 'retention-announcement.txt' announcing the updated guide.",
    ]
    for prompt in prompts:
        print(f"\n💬 {prompt}")
        result = await agent.run(prompt)
        print(f"🤖 {result}")


asyncio.run(main())
