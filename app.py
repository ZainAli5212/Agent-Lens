"""
AgentLens — CLI Entry Point
Run: python app.py
"""
import sys
from agent_core import search_llms
from ollama_utils import get_local_models, filter_agentic_models, is_ollama_running
from display import (
    print_banner,
    print_recommendations,
    print_local_models,
    print_comparison_table,
    print_error,
    print_status,
    print_divider,
    BOLD, CYAN, DIM, RESET, YELLOW, GREEN,
)

EXAMPLE_QUERIES = [
    "I'm building a marketing automation agent for campaign creation and report generation.",
    "Best LLMs for a customer support agentic workflow with tool calling.",
    "Which models are best for a coding assistant agent that runs tests and fixes bugs?",
]

HISTORY: list[str] = []


def prompt_user() -> str:
    print(f"\n{DIM}Examples:{RESET}")
    for i, ex in enumerate(EXAMPLE_QUERIES, 1):
        print(f"  {DIM}{i}. {ex}{RESET}")
    print()
    try:
        query = input(f"{BOLD}{CYAN}Describe your agentic workflow{RESET} "
                      f"{DIM}(or 'quit' / 'history'){RESET}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
        sys.exit(0)
    return query


def show_history():
    if not HISTORY:
        print(f"\n{DIM}  No queries yet in this session.{RESET}\n")
        return
    print(f"\n{BOLD}{YELLOW}Session History:{RESET}")
    for i, q in enumerate(HISTORY, 1):
        print(f"  {i}. {q}")
    print()


def run():
    print_banner()

    # ── Startup status ──────────────────────────────────────────────────────
    ollama_ok    = is_ollama_running()
    local_models = filter_agentic_models(get_local_models()) if ollama_ok else []
    print_status(openai_ok=True, ollama_ok=ollama_ok, model_count=len(local_models))

    # ── Main CLI loop (bounded — exits on quit/EOF/Ctrl-C, not infinite) ───
    while True:
        query = prompt_user()

        if not query:
            continue

        if query.lower() in ("quit", "exit", "q"):
            print(f"\n{GREEN}Goodbye!{RESET}\n")
            break

        if query.lower() in ("history", "h"):
            show_history()
            continue

        HISTORY.append(query)
        print(f"\n{DIM}  Searching for LLMs suited to your workflow…{RESET}")

        # ── Agent call ──────────────────────────────────────────────────────
        result = search_llms(query, verbose=True)

        if result is None:
            print_error("Could not retrieve recommendations. "
                        "Check your model/API settings in .env")
            continue

        recs = result.get("recommendations", [])

        if not recs:
            print_error("The model returned no recommendations. Try rephrasing your query.")
            continue

        # ── Display ─────────────────────────────────────────────────────────
        print_recommendations(result)
        print_comparison_table(recs)
        print_local_models(local_models)

        print_divider("─", colour=DIM)
        print(f"  {DIM}Type another query, 'history', or 'quit'.{RESET}")


if __name__ == "__main__":
    run()
