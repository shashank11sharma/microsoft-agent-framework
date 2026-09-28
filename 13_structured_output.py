# ============================================================
# 13 - Structured Output / Response Models
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv
from pydantic import BaseModel

# --- SECTION 2: CONFIGURATION ---
load_dotenv()
client = OpenAIChatClient()


# --- SECTION 3: PYDANTIC RESPONSE MODELS ---
class ContentReviewResult(BaseModel):
    review_status: str  # "approved", "needs_changes", or "escalate"
    confidence: float  # 0.0 – 1.0
    key_phrases: list[str]  # words/phrases driving the sentiment
    summary: str  # one-sentence summary


class PublicationPlan(BaseModel):
    goal: str
    steps: list[str]
    estimated_days: int
    blockers: list[str]


# --- SECTION 4: AGENTS WITH response_format ---
# Passing response_format tells the model to always return valid JSON
# matching that schema — no more regex parsing or string manipulation.
content_review_agent = Agent(
    client=client,
    name="ContentReviewAgent",
    instructions=("You review SharePoint document feedback. " "Classify its status and return a structured result."),
    default_options={
        "response_format": ContentReviewResult,
    },
)

publication_planner_agent = Agent(
    client=client,
    name="PublicationPlanner",
    instructions=("You plan Microsoft 365 content publishing. " "Break down the goal into a concrete, actionable plan."),
    default_options={
        "response_format": PublicationPlan,
    },
)


# --- SECTION 5: HELPERS ---
async def analyze_content_review(text: str) -> ContentReviewResult:
    response = await content_review_agent.run(f"Classify this SharePoint document review comment:\n\n{text}")
    return ContentReviewResult.model_validate_json(response.text)


async def build_publication_plan(goal: str) -> PublicationPlan:
    response = await publication_planner_agent.run(f"Create a Microsoft 365 content-publishing plan for: {goal}")
    return PublicationPlan.model_validate_json(response.text)


# --- SECTION 6: RUN & TEST ---
async def main():
    reviews = [
        "Approved. The retention guide has an owner, a review date, and the correct label.",
        "Needs changes: the draft contains personal data and has no retention label.",
        "Please escalate this policy because the document owner is unknown.",
    ]

    print("=" * 60)
    print("📊 SHAREPOINT CONTENT REVIEW")
    print("=" * 60)
    for review in reviews:
        result = await analyze_content_review(review)
        print(f"\n📝 Review: {review[:60]}...")
        print(f"   Status     : {result.review_status.upper()} ({result.confidence:.0%} confident)")
        print(f"   Key phrases: {', '.join(result.key_phrases)}")
        print(f"   Summary    : {result.summary}")
        print("-" * 60)

    print("\n" + "=" * 60)
    print("🗂️  PUBLICATION PLAN")
    print("=" * 60)
    plan = await build_publication_plan("Publish the new retention guide in SharePoint and announce it in Teams")
    print(f"\n🎯 Goal: {plan.goal}")
    print(f"⏱️  Estimated days: {plan.estimated_days}")
    print("📋 Steps:")
    for i, step in enumerate(plan.steps, 1):
        print(f"   {i}. {step}")
    if plan.blockers:
        print(f"⚠️  Blockers: {', '.join(plan.blockers)}")


asyncio.run(main())
