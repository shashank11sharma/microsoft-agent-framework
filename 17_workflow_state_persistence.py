# ============================================================
# 17 - Workflow State Persistence
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio

from agent_framework import Agent, AgentResponse, FileCheckpointStorage
from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import SequentialBuilder
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()

CHECKPOINT_PATH = ".wf_checkpoints"  # multi-agent workflow checkpoint persistence


# --- SECTION 3: WORKFLOW CHECKPOINT PERSISTENCE ---
# FileCheckpointStorage saves the full workflow state after each agent step.
# If the process crashes mid-pipeline, resume from the last checkpoint
# by passing checkpoint_id= to workflow.run().
researcher = Agent(
    client=client,
    name="LibraryAnalyst",
    instructions=(
        "You are a shared-document organization analyst. Given a general topic, return 5 concise, "
        "practical suggestions about clear titles, folders, owners, and update dates. Keep them neutral and general."
    ),
)
writer = Agent(
    client=client,
    name="PublishingWriter",
    instructions=(
        "You are a knowledge-base writer. Turn the suggestions into a concise, neutral guide for organizing shared team documents. "
        "Use only the information provided and do not claim access to real files or services. Return only the guide."
    ),
)

checkpoint_storage = FileCheckpointStorage(CHECKPOINT_PATH)

workflow = SequentialBuilder(
    participants=[
        researcher,
        writer,
    ],
    output_from="all",
    checkpoint_storage=checkpoint_storage,
).build()


# --- SECTION 4: DEMO HELPERS ---
async def demo_workflow_checkpoints():
    print("\n" + "=" * 60)
    print("🗂️  WORKFLOW CHECKPOINTS — FileCheckpointStorage")
    print("=" * 60)

    topic = "Practical ways to organize a shared team document library"
    print(f"\n🚀 Running pipeline for: '{topic}'")

    result = await workflow.run(topic)
    outputs = result.get_outputs()
    for agent_response in outputs:
        agent_response: AgentResponse = agent_response
        for msg in agent_response.messages:
            name = msg.author_name or "assistant"
            print(f"\n[{name}]\n{msg.text}")

    # Show saved checkpoints so viewer can see they're on disk
    print("Workflow name:", workflow.name)
    saved = await checkpoint_storage.list_checkpoints(workflow_name=workflow.name)
    print(f"\n📌 {len(saved)} checkpoint(s) saved to '{CHECKPOINT_PATH}/'")
    if saved:
        latest = saved[-1]
        print(f"   Latest ID : {latest.checkpoint_id}")
        print(f"   Timestamp : {latest.timestamp}")
        print("\n💡 To resume from this checkpoint, pass:")
        print(f"   workflow.run(checkpoint_id='{latest.checkpoint_id}')")


# --- SECTION 5: RUN & TEST ---
async def main():
    await demo_workflow_checkpoints()


asyncio.run(main())
