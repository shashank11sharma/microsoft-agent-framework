# ============================================================
# 09 - Concurrent / Fan-Out Workflows
# ============================================================

# --- SECTION 1: IMPORTS ---
import asyncio
import time

from agent_framework import AgentResponse
from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import ConcurrentBuilder
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()

# --- SECTION 3: PARALLEL AGENTS ---
hindi_translator = client.as_agent(
    name="HindiMetadataTranslator",
    instructions="Translate the given document metadata from English to Hindi. Return ONLY the translation.",
)
kannada_translator = client.as_agent(
    name="KannadaMetadataTranslator",
    instructions="Translate the given document metadata from English to Kannada. Return ONLY the translation.",
)
french_translator = client.as_agent(
    name="FrenchMetadataTranslator",
    instructions="Translate the given document metadata from English to French. Return ONLY the translation.",
)
sentiment_analyzer = client.as_agent(
    name="ContentRiskReviewer",
    instructions=(
        "Assess the governance risk of the given SharePoint document description. "
        'Return JSON only: {"risk": "low|medium|high", "confidence": 0.0-1.0, "reason": "..."}'
    ),
)
keyword_extractor = client.as_agent(
    name="MetadataKeywordExtractor",
    instructions="Extract the top 5 SharePoint search keywords from the given document description. Return a comma-separated list.",
)

# --- SECTION 4: BUILD AND RUN WORKFLOW ---
workflow = ConcurrentBuilder(
    participants=[
        hindi_translator,
        kannada_translator,
        french_translator,
        sentiment_analyzer,
        keyword_extractor,
    ]
).build()


async def main():
    text = "The approved retention guide is owned by Records Management, reviewed annually, and stored in the Policy Hub SharePoint library."
    print(f"📥 Input: {text}\n")
    print("🔀 Running 5 agents in parallel...\n")

    start = time.time()
    events = await workflow.run(text)
    elapsed = time.time() - start

    outputs = events.get_outputs()
    if outputs:
        final: AgentResponse = outputs[0]
        for msg in final.messages:
            name = msg.author_name or "assistant"
            print(f"[{name}]\n{msg.text}\n")

    print(f"⏱  Total time (parallel): {elapsed:.2f}s")
    print(f"💡 Sequential would take ~{elapsed * 5:.1f}s — 5× slower!")


asyncio.run(main())
