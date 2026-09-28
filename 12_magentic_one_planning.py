# ============================================================
# 12 - Magentic-One Orchestration Pattern
# ============================================================

# --- SECTION 1: IMPORTS ---
import asyncio

from agent_framework import Agent, AgentResponse
from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import MagenticBuilder
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()

# --- SECTION 3: SPECIALIST AGENTS ---
content_researcher = Agent(
    client=client,
    name="ContentResearcher",
    instructions="You research the supplied source material and return structured content-management findings with key facts.",
)
metadata_planner = Agent(
    client=client,
    name="MetadataPlanner",
    instructions="You propose useful SharePoint metadata, ownership, and retention fields for the requested content.",
)
publication_writer = Agent(
    client=client,
    name="PublicationWriter",
    instructions="You turn research and metadata guidance into clear SharePoint pages and concise Teams announcements.",
)
quality_critic = Agent(
    client=client,
    name="QualityCritic",
    instructions=(
        "You review outputs for accuracy, completeness, and clarity. "
        "Return PASS if good, or list specific FIXES needed."
    ),
)
orchestrator = Agent(
    client=client,
    name="Orchestrator",
    instructions=(
        "You are a Magentic-One orchestrator. Plan which specialist agents to invoke "
        "and in what order to complete the task. Re-plan dynamically based on results."
        "Perform this task under 60 seconds."
    ),
)

# --- SECTION 4: MAGENTIC-ONE ---
# Plans which agents to use, in what order, re-plans dynamically.
workflow = MagenticBuilder(
    participants=[
        content_researcher,
        metadata_planner,
        publication_writer,
        quality_critic,
    ],
    manager_agent=orchestrator,
).build()


# --- SECTION 5: RUN & TEST ---
async def main():
    task = (
        "Create a content-publishing playbook for a new SharePoint policy library. Include: "
        "1) A document intake and review process, "
        "2) Suggested metadata and retention fields, "
        "3) A Teams announcement draft and Outlook review-meeting agenda, "
        "4) Three governance best practices."
    )
    print("=" * 60)
    print(f"🎯 Task: {task}\n")
    print("🧠 Magentic-One planning and executing...\n")

    events = await workflow.run(task)
    outputs = events.get_outputs()
    if outputs:
        final: AgentResponse = outputs[0]
        for msg in final.messages:
            print(msg.text)


asyncio.run(main())
