# ============================================================
# 05 - Local MCP Server using FastMCP (stdio transport)
# ============================================================

import datetime
import json
import os
import sys

from fastmcp import FastMCP

# --- SECTION 1: CREATE SERVER ---
mcp = FastMCP(name="m365-content-tools")


# --- SECTION 2: DEFINE TOOLS ---
@mcp.tool()
def get_outlook_calendar_events() -> str:
    """Returns mock Outlook calendar events for the content team."""
    return json.dumps(
        [
            {"subject": "SharePoint policy review", "date": "2026-10-01", "time": "10:00"},
            {"subject": "Content publishing check-in", "date": "2026-10-02", "time": "14:30"},
        ],
        indent=2,
    )


@mcp.tool()
def calculate(expression: str) -> str:
    """Evaluates a safe math expression and returns the result.

    Args:
        expression: Math expression e.g. '2 + 2' or '10 ** 3'
    """
    try:
        value = eval(expression, {"__builtins__": {}})
        return f"{expression} = {value}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def list_sharepoint_library(path: str) -> str:
    """Lists files in a local folder standing in for a SharePoint library.

    Args:
        path: Local demo library path, e.g. '05_mcp_integration/demo_library'
    """
    try:
        entries = sorted(os.listdir(path))
        lines = [f"{'📁' if os.path.isdir(os.path.join(path, e)) else '📄'} {e}" for e in entries]
        return f"Contents of '{path}':\n" + "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def read_sharepoint_document(filepath: str) -> str:
    """Reads a local demo document standing in for a SharePoint file.

    Args:
        filepath: Path to the file to read
    """
    try:
        with open(filepath, "r") as f:
            return f"Contents of '{filepath}':\n{f.read()}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def write_sharepoint_demo_document(filepath: str, content: str) -> str:
    """Writes a local demo file; this does not publish to SharePoint.

    Args:
        filepath: Path to write to
        content: Text content to write
    """
    try:
        with open(filepath, "w") as f:
            f.write(content)
        return f"✅ Written {len(content)} chars to '{filepath}'"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_teams_channel_messages(channel: str) -> str:
    """Returns mock recent messages from a Teams channel.

    Args:
        channel: Channel name, e.g. 'Content-Governance'
    """
    messages = {
        "content-governance": [
            "Please review the retention guide before publishing.",
            "Each policy document needs a named owner.",
        ],
        "project-atlas": ["The project plan is ready for review."],
    }
    return json.dumps(messages.get(channel.lower(), []), indent=2)


# --- SECTION 3: START SERVER ---
if __name__ == "__main__":
    print("FastMCP Microsoft 365 content demo started (6 tools available).", file=sys.stderr, flush=True)
    mcp.run(transport="stdio")
