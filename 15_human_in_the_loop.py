# ============================================================
# 15 - Human-in-the-Loop
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio
from collections.abc import Awaitable, Callable
from typing import Annotated

from agent_framework import (
    Agent,
    FunctionInvocationContext,
    FunctionMiddleware,
    MiddlewareTermination,
)
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()


# --- SECTION 3: APPROVAL MIDDLEWARE ---
# Intercepts every tool call and pauses for human confirmation.
# If the human denies, MiddlewareTermination stops the tool and
# passes a rejection message back to the agent so it can respond gracefully.
class HumanApprovalMiddleware(FunctionMiddleware):
    def __init__(self, tools_requiring_approval: set[str] | None = None):
        # None = require approval for ALL tools
        self.tools_requiring_approval = tools_requiring_approval

    async def process(
        self,
        context: FunctionInvocationContext,
        call_next: Callable[[], Awaitable[None]],
    ):
        print("In the Middleware")
        tool_name = context.function.name
        needs_approval = tool_name in self.tools_requiring_approval

        if not needs_approval:
            await call_next()
            return

        print(f"\n  🔔 Tool requested: {tool_name}")
        print(f"     Arguments    : {context.arguments}")
        decision = input("  ✅ Allow? (y/n): ").strip().lower()

        if decision != "y":
            print(f"  🚫 Human denied '{tool_name}'.")
            context.result = f"[Action '{tool_name}' was denied by the user. Do not retry it.]"
            raise MiddlewareTermination()

        print(f"  ✅ Approved — executing '{tool_name}'...")
        await call_next()


# --- SECTION 4: SENSITIVE TOOLS ---
def post_teams_announcement(
    channel: Annotated[str, "Teams channel name"],
    subject: Annotated[str, "Announcement title"],
    body: Annotated[str, "Announcement body content"],
) -> str:
    """Simulates posting an announcement to a Teams channel."""
    return f"✅ Teams announcement posted to {channel} | Title: '{subject}' | Body: '{body}'"


def delete_sharepoint_document(document_id: Annotated[str, "SharePoint document ID, e.g. 'POL-OLD-1'"]) -> str:
    """Simulates deleting a SharePoint document."""
    return f"✅ Deleted SharePoint document: {document_id}"


def read_sharepoint_document(document_id: Annotated[str, "SharePoint document ID, e.g. 'POL-104'"]) -> str:
    """Returns mock contents for a SharePoint document."""
    return f"[SharePoint document {document_id}]: Review retention labels with the owner every 12 months."


# --- SECTION 5: AGENT ---
# Only destructive / irreversible tools require approval.
# read_sharepoint_document is considered safe and runs without prompting.
agent = Agent(
    client=client,
    name="AssistantWithOversight",
    instructions=(
        "You are a Microsoft 365 content assistant that can post Teams announcements, delete SharePoint documents, and read SharePoint documents. "
        "The tools are demo simulations, not connected to a tenant. "
        "Available tools: 'post_teams_announcement', 'delete_sharepoint_document', 'read_sharepoint_document'."
    ),
    tools=[post_teams_announcement, delete_sharepoint_document, read_sharepoint_document],
    middleware=[HumanApprovalMiddleware(tools_requiring_approval={"post_teams_announcement", "delete_sharepoint_document"})],
)


# --- SECTION 6: RUN & TEST ---
async def main():
    print("=" * 60)
    print("🔒 Human-in-the-Loop Demo")
    print("   Irreversible tools pause for your approval.")
    print("=" * 60)

    tasks = [
        "Read SharePoint document POL-104 and summarize its review requirement.",
        "Post a Teams announcement in Content-Governance titled 'Retention guide updated' with body 'Please review the latest approved guide in Policy Hub.'",
        "Delete obsolete SharePoint document POL-OLD-1.",
    ]

    for task in tasks:
        print(f"\n💬 Task: {task}")
        session = agent.create_session()
        response = await agent.run(task, session=session)
        print(f"🤖 {response.text}")
        print("-" * 55)


asyncio.run(main())
