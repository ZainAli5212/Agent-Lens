"""
AgentLens — CLI Display Helpers
Pretty-prints results to the terminal without any external UI library.
"""

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

# Foreground colours
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"
MAGENTA= "\033[95m"
WHITE  = "\033[97m"

# Background
BG_DARK = "\033[40m"


def _bar(score: int, width: int = 10) -> str:
    """Render a simple ASCII progress bar for a 0-10 score."""
    filled = round(score / 10 * width)
    bar    = "█" * filled + "░" * (width - filled)
    colour = GREEN if score >= 8 else YELLOW if score >= 5 else RED
    return f"{colour}{bar}{RESET} {BOLD}{score}/10{RESET}"


def _cost_badge(tier: str) -> str:
    colours = {
        "free":   GREEN,
        "low":    CYAN,
        "medium": YELLOW,
        "high":   RED,
    }
    c = colours.get(tier.lower(), WHITE)
    return f"{c}[{tier.upper()}]{RESET}"


def _tool_badge(tool_calling: str) -> str:
    if tool_calling.lower().startswith("yes"):
        return f"{GREEN}✔ {tool_calling}{RESET}"
    return f"{RED}✘ {tool_calling}{RESET}"


def print_banner():
    print(f"""
{CYAN}{BOLD}
  ██████╗  ██████╗ ███████╗███╗   ██╗████████╗██╗     ███████╗███╗   ██╗███████╗
 ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██║     ██╔════╝████╗  ██║██╔════╝
 ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ██║     █████╗  ██╔██╗ ██║███████╗
 ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██║     ██╔══╝  ██║╚██╗██║╚════██║
 ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ███████╗███████╗██║ ╚████║███████║
 ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝
{RESET}{DIM}  AI-Powered LLM Discovery Assistant for Agentic AI Workflows{RESET}
""")


def print_divider(char="─", width=72, colour=DIM):
    print(f"{colour}{char * width}{RESET}")


def print_recommendations(data: dict):
    """Render the full recommendations from the parsed agent response."""
    recs = data.get("recommendations", [])
    summary = data.get("query_summary", "")

    print(f"\n{BOLD}{CYAN}Query Summary:{RESET} {summary}\n")
    print_divider("═", colour=CYAN)

    for i, model in enumerate(recs, start=1):
        score = model.get("suitability_score", 0)
        print(f"\n{BOLD}{WHITE} #{i}  {CYAN}{model['name']}{RESET}  "
              f"{DIM}by {model.get('provider','?')}{RESET}  "
              f"{_cost_badge(model.get('cost_tier','?'))}")
        print_divider()

        print(f"  {DIM}Description  :{RESET} {model.get('description','')}")
        print(f"  {DIM}Parameters   :{RESET} {BOLD}{model.get('parameters','N/A')}{RESET}")
        print(f"  {DIM}Context      :{RESET} {model.get('context_window','N/A')}")
        print(f"  {DIM}Tool Calling :{RESET} {_tool_badge(model.get('tool_calling','No'))}")
        print(f"  {DIM}Suitability  :{RESET} {_bar(score)}")

        features = model.get("key_features", [])
        if features:
            print(f"  {DIM}Key Features :{RESET}")
            for feat in features:
                print(f"    {GREEN}•{RESET} {feat}")

    print()
    print_divider("═", colour=CYAN)


def print_local_models(local_models: list[dict]):
    """Render the Ollama local models section."""
    print(f"\n{BOLD}{MAGENTA}📦  Local Ollama Models{RESET}")
    print_divider(colour=MAGENTA)

    if not local_models:
        print(f"  {DIM}No local models found (is Ollama running?){RESET}\n")
        return

    # Header
    print(f"  {BOLD}{'Name':<30} {'Size (GB)':>10} {'Params':>10} "
          f"{'Quant':>10} {'Agentic?':>10}{RESET}")
    print_divider("·", colour=DIM)

    for m in local_models:
        agentic = (f"{GREEN}✔ Yes{RESET}" if m.get("agentic_suitable")
                   else f"{DIM}  —  {RESET}")
        print(f"  {CYAN}{m['name']:<30}{RESET} "
              f"{m['size_gb']:>10.2f} "
              f"{m['parameter_size']:>10} "
              f"{m['quantization']:>10} "
              f"  {agentic}")
    print()


def print_comparison_table(recs: list[dict]):
    """Print a compact side-by-side comparison table."""
    print(f"\n{BOLD}{YELLOW}📊  Comparison Table{RESET}")
    print_divider(colour=YELLOW)

    header = (f"  {BOLD}{'#':>2}  {'Model':<25} {'Provider':<12} "
              f"{'Params':<12} {'Tool?':<6} {'Cost':<8} {'Score':>5}{RESET}")
    print(header)
    print_divider("·", colour=DIM)

    for i, m in enumerate(recs, 1):
        tool_ok = "✔" if m.get("tool_calling","").lower().startswith("yes") else "✘"
        tool_col = f"{GREEN}{tool_ok}{RESET}" if tool_ok == "✔" else f"{RED}{tool_ok}{RESET}"
        score_col = (f"{GREEN}" if m.get("suitability_score",0) >= 8
                     else f"{YELLOW}") + f"{m.get('suitability_score',0):>5}{RESET}"
        print(f"  {i:>2}  {CYAN}{m['name']:<25}{RESET} "
              f"{m.get('provider',''):<12} "
              f"{m.get('parameters','N/A'):<12} "
              f"  {tool_col}    "
              f"{m.get('cost_tier','?'):<8} "
              f"{score_col}")
    print()


def print_error(msg: str):
    print(f"\n{RED}{BOLD}[ERROR]{RESET} {msg}\n")


def print_status(openai_ok: bool, ollama_ok: bool, model_count: int):
    oa = f"{GREEN}✔ Connected{RESET}" if openai_ok else f"{RED}✘ Unreachable{RESET}"
    ol = f"{GREEN}✔ Running{RESET}"   if ollama_ok else f"{RED}✘ Not running{RESET}"
    print(f"\n{DIM}  OpenAI/Ollama API : {oa}   "
          f"Ollama Server : {ol}   "
          f"Local Models : {BOLD}{model_count}{RESET}{DIM} installed{RESET}\n")
