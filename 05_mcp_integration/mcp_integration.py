# ============================================================
# 05 - MAF Agent using Local FastMCP stdio Server
# ============================================================

# --- SECTION 1: IMPORTS ---
import asyncio
import sys

from agent_framework import Agent, MCPStdioTool
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# --- SECTION 2: CONFIGURATION ---
load_dotenv()


# --- SECTION 3: RUN ---
async def main():
    async with (
        MCPStdioTool(
            name="m365-content-tools",  # must match FastMCP server name
            command=sys.executable,  # path to current Python interpreter
            args=["05_mcp_integration/mcp_server.py"],  # your FastMCP server script
        ) as mcp_tool,
        Agent(
            client=OpenAIChatClient(),
            name="MCPAgent",
            instructions=(
                "You are a content-management assistant using local Microsoft 365 demo tools via MCP. "
                "The SharePoint library is represented by local files; Teams and Outlook data are mock fixtures. "
                "Use the available tools to inspect and update demo documents, check calendar events, and read channel messages. "
                "Never guess document contents — always read them."
            ),
        ) as agent,
    ):
        prompts = [
            "Show the Outlook calendar events for the content review.",
            "List the SharePoint demo library files (path = '05_mcp_integration/demo_library').",
            "Write a local SharePoint demo document '05_mcp_integration/demo_library/retention-guide.txt' with content: 'Review retention labels every year.'",
            "Read the local SharePoint demo document '05_mcp_integration/demo_library/retention-guide.txt'.",
            "Show recent messages in the Teams Content-Governance channel.",
            "Calculate how many weeks are in 365 days, using 7 days per week.",
        ]

        for prompt in prompts:
            print(f"\n💬 Shashank: {prompt}")
            # tools passed to agent.run() — NOT to Agent() constructor
            result = await agent.run(prompt, tools=mcp_tool)
            print(f"🤖 Agent: {result}")
            input()


asyncio.run(main())
