# Microsoft Agent Framework Series

This repository demonstrates Microsoft Agent Framework patterns through a shared Microsoft 365 content-management scenario. The examples cover SharePoint document libraries, Teams review and announcements, and Outlook calendar coordination.

The Microsoft 365 services are simulated: tools return mock data or use local demo files. No example connects to a tenant or calls Microsoft Graph.

## Setup

Use Python 3.13 or newer, create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and edit it with your model credentials and deployment settings:

```powershell
Copy-Item .env.example .env
```

For Microsoft Foundry, set `OPENAI_BASE_URL` to the resource's OpenAI-compatible inference endpoint, such as `https://<resource>.services.ai.azure.com/openai/v1/`. Use your resource key and deployed model name. Do not use the project URL under `/api/projects/`. The `.env` file is excluded from version control.

## Examples

Each filename is a link to the source file. On GitHub, select a link to open that example.

1. **[First agent](01_first_agent.py)**: Loads configuration, creates one agent with SharePoint content-management instructions, sends it a policy-announcement request, and prints the response. This is the basic model → agent → single request flow.
2. **[Agent instructions](02_agent_instructions.py)**: Sends a content question to three agents with different roles: policy writer, employee onboarding assistant, and governance reviewer. The comparison shows how instructions change the response while the shared client and input data stay the same.
3. **[Sessions and conversations](03_multi_turn_conversation.py)**: Runs requests first without a session, then with a conversation session, and finally with two separate sessions. The separate SharePoint library details demonstrate how each session keeps its own conversation history.
4. **[Tool calling](04_tool_calling.py)**: Gives the agent calendar, calculator, mock SharePoint search, mock Teams messages, and local draft-saving functions. The model chooses tools from the request, receives their results, and uses them to form a reply.
5. **[MCP integration client](05_mcp_integration/mcp_integration.py)** and **[MCP server](05_mcp_integration/mcp_server.py)**: Starts a local FastMCP server over stdio and passes its tools to the agent at run time. The server represents SharePoint with local demo files and supplies mock Teams and Outlook data; it does not connect to a tenant.
6. **[Context providers](06_context_provider_agent_memory.py)**: Defines providers that inject FAQ instructions and a local content catalog before each run. The assistant answers from this supplied SharePoint-style context and escalates questions the context cannot answer.
7. **[Middleware](07_middleware.py)**: Wraps each agent run with logging, a content-safety check, and response post-processing. A normal request continues through the chain; an unsafe sharing request is blocked before the model runs.
8. **[Sequential workflow](08_sequential_multi_agent.py)**: Passes a policy topic through a researcher, summarizer, and Teams announcement writer in order. Intermediate results from one agent become the next agent's input.
9. **[Concurrent fan-out](09_concurrent_fan_out.py)**: Sends the same document description to five independent agents for translation, governance-risk review, and keyword extraction. Their results are collected after the parallel workflow completes.
10. **[Conditional routing](10_conditional_routing.py)**: A router classifies each request as SharePoint, Teams, Outlook, or general governance, then the code selects the matching specialist from a route map. Unknown classifications safely fall back to the general agent.
11. **[Writer-critic loop](11_writer_critic_feedback.py)**: A writer creates a SharePoint knowledge-base draft, a critic returns a score and specific feedback, and the writer revises using the same session. The loop stops at the approval score or its iteration limit.
12. **[Magentic-One planning](12_magentic_one_planning.py)**: A manager agent plans and coordinates content research, metadata planning, publication writing, and quality review. Magentic-One can adjust the specialist sequence as it receives results.
13. **[Structured output](13_structured_output.py)**: Uses Pydantic response models for content-review results and publication plans. The agent returns schema-shaped JSON, which the script validates and then prints field by field.
14. **[Error handling and retries](14_error_handling_retries.py)**: Simulates transient SharePoint and Outlook failures, retries agent and function calls through middleware, and returns a fallback when a tool exhausts its retries. This illustrates resilience without changing the request workflow.
15. **[Human approval](15_human_in_the_loop.py)**: Intercepts simulated Teams announcements and SharePoint deletions for an interactive yes/no decision, while document reads proceed without approval. A denial returns a message to the agent instead of running the action.
16. **[Agent state persistence](16_single_agent_state_persistence.py)**: Stores conversation history with `FileHistoryProvider` under a stable session ID. Run the script again to see the agent reuse saved SharePoint migration context across process restarts.
17. **[Workflow state persistence](17_workflow_state_persistence.py)**: Runs a two-agent library-analysis and publishing workflow with `FileCheckpointStorage`. It lists the saved checkpoint and shows how to resume the workflow by checkpoint ID.
18. **[Evaluation and testing](18_evaluation_testing.py)**: Evaluates a mock SharePoint assistant with local checks for metadata keywords and whether the search tool was called. It runs the checks separately and together against a small set of test queries.
19. **[Production API](19_production_deployment.py)**: Wraps a content assistant in FastAPI with health, JSON chat, and server-sent-event streaming endpoints. The API shape is runnable locally, while SharePoint, Teams, and Outlook tool responses remain simulated.

## Dependencies

Install packages with `pip install -r requirements.txt`.

