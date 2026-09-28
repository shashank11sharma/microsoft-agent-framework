# ============================================================
# 06 - Context Providers & Agent Memory
# ============================================================


# --- SECTION 1: IMPORTS ---
import asyncio
from typing import Any

from agent_framework import Agent, AgentSession, ContextProvider, SessionContext
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()


# --- SECTION 3: CUSTOM CONTEXT PROVIDERS ---
class FAQContextProvider(ContextProvider):
    """Injects static FAQ text as instructions before every agent run."""

    def __init__(self, faq_text: str):
        super().__init__("faq-provider")
        self._faq = faq_text

    async def before_run(
        self,
        *,
        agent: Any,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        context.extend_instructions(self.source_id, self._faq)


class FileContextProvider(ContextProvider):
    """Reads a file and injects its contents as instructions before every run."""

    def __init__(self, filepath: str):
        super().__init__("file-provider")
        self._filepath = filepath

    async def before_run(
        self,
        *,
        agent: Any,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        try:
            with open(self._filepath, "r") as f:
                content = f.read()
            context.extend_instructions(self.source_id, content)
        except FileNotFoundError:
            pass


# --- SECTION 4: SETUP ---
with open("product_catalog.txt", "w") as f:
    f.write(
        """
        SHAREPOINT CONTENT CATALOG — Contoso
        - Retention Guide: Policy Hub | Owner: Records Team | Review: 2026-10-01
        - Project Atlas Plan: Projects | Owner: Atlas PMO | Status: In review
        - Brand Assets: Communications | Owner: Marketing | Status: Approved
        """
    )

faq_provider = FAQContextProvider(
    """
    MICROSOFT 365 CONTENT FAQ — Contoso
    - SharePoint policy library: Policy Hub
    - Teams review channel: Content-Governance
    - Outlook review calendar: Content Reviews
    - Document owners must review policies every 12 months.
    - Drafts must be approved before they are announced in Teams.
    """
)
catalog_provider = FileContextProvider("product_catalog.txt")

support_agent = Agent(
    client=OpenAIChatClient(),
    name="ContentHelpAgent",
    instructions=(
        "You are a content-management assistant for Contoso. "
        "Answer ONLY using the context provided to you. "
        "If the answer is not in the context, say: 'I will ask the content owner to confirm.'"
    ),
    context_providers=[faq_provider, catalog_provider],
)


# --- SECTION 5: RUN & TEST ---
async def main():
    questions = [
        "Which SharePoint library stores policies?",
        "Which Teams channel is used for content reviews?",
        "Who owns the Project Atlas plan?",
        "How often should policy documents be reviewed?",
        "Which library contains approved brand assets?",
    ]
    for query in questions:
        print(f"\n❓ {query}")
        r = await support_agent.run(query)
        print(f"💬 {r}")


asyncio.run(main())
