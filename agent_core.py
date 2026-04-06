"""
AgentLens — Core Agent Logic
Uses the OpenAI Python SDK (chat.completions) with a DDGS web_search function tool.
Implements a tool-call loop (no infinite loop, bounded by MAX_TOOL_ROUNDS).
"""
import json
from openai import OpenAI
from ddgs import DDGS

from config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    CHAT_MODEL,
    MAX_SEARCH_RESULTS,
    SYSTEM_PROMPT,
)

# ── OpenAI client (points to local Ollama or real OpenAI) ──────────────────────
client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

MAX_TOOL_ROUNDS = 5  # safety cap — prevents runaway loops

# ── Tool definitions ────────────────────────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web using DuckDuckGo for current information about "
                "LLMs, AI models, benchmarks, pricing, and capabilities."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Max number of results to return.",
                        "default": MAX_SEARCH_RESULTS,
                    },
                },
                "required": ["query"],
            },
        },
    }
]


# ── Tool executor ───────────────────────────────────────────────────────────────
def run_web_search(query: str, max_results: int = MAX_SEARCH_RESULTS) -> str:
    """Execute a DuckDuckGo text search and return formatted results."""
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "No results found."
        formatted = "\n\n".join(
            f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}"
            for r in results
        )
        return formatted
    except Exception as e:
        return f"Search error: {e}"


def dispatch_tool(tool_name: str, arguments: dict) -> str:
    """Route a tool call to the correct executor."""
    if tool_name == "web_search":
        return run_web_search(**arguments)
    return f"Unknown tool: {tool_name}"


# ── Main agent function ─────────────────────────────────────────────────────────
def search_llms(user_query: str, verbose: bool = True) -> dict | None:
    """
    Run the AgentLens discovery loop for a given user query.

    1. Send user message + system prompt to the model.
    2. If the model requests tool calls, execute them and feed results back.
    3. Repeat up to MAX_TOOL_ROUNDS times.
    4. Parse and return the final JSON response.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_query},
    ]

    for round_num in range(1, MAX_TOOL_ROUNDS + 1):
        if verbose:
            print(f"\n  [round {round_num}] Calling model...", flush=True)

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        message = response.choices[0].message

        # ── No tool calls → model produced its final answer ──────────────────
        if not message.tool_calls:
            raw = message.content or ""
            return _parse_json_response(raw)

        # ── Model wants to call one or more tools ─────────────────────────────
        # Append the assistant message (with tool_calls) to history
        messages.append({
            "role":       "assistant",
            "content":    message.content or "",
            "tool_calls": [
                {
                    "id":       tc.id,
                    "type":     "function",
                    "function": {
                        "name":      tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ],
        })

        # Execute each tool and append results
        for tc in message.tool_calls:
            tool_name = tc.function.name
            try:
                arguments = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                arguments = {}

            if verbose:
                query_preview = arguments.get("query", tool_name)
                print(f"  [tool] {tool_name}({query_preview!r})", flush=True)

            result = dispatch_tool(tool_name, arguments)

            messages.append({
                "role":         "tool",
                "tool_call_id": tc.id,
                "content":      result,
            })

    # Exhausted rounds without a final answer
    if verbose:
        print("  [warn] Reached max tool rounds without a final answer.")
    return None


# ── JSON parsing helper ─────────────────────────────────────────────────────────
def _parse_json_response(raw: str) -> dict | None:
    """
    Strip optional markdown fences and parse JSON.
    Returns the parsed dict, or None on failure.
    """
    # Remove ```json ... ``` fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        # Drop first and last fence lines
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        cleaned = "\n".join(inner).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"  [error] Failed to parse model response as JSON: {e}")
        print(f"  [raw]   {raw[:300]}...")
        return None
