# AgentLens 🔍
**AI-Powered LLM Discovery Assistant for Agentic AI Workflows**

AgentLens takes a plain-English description of your workflow, searches for current model information, and returns a ranked shortlist of LLMs that fit the task.

It is designed for questions like:

- Which models are good for a tool-calling customer support agent?
- What is the best open-source model for a coding assistant?
- Which LLMs have enough context for long-running research workflows?

## What It Does

- Accepts a natural-language workflow description from the terminal.
- Uses DuckDuckGo search to gather up-to-date model information.
- Produces a structured set of recommendations with suitability scores.
- Supports local Ollama models and hosted OpenAI-compatible endpoints.
- Keeps a simple session history so you can compare prompts during one run.

## Requirements

- Python 3.11 or newer.
- `uv` installed locally.
- Ollama installed and running if you want to use local models.
- An OpenAI-compatible API endpoint if you want to target a remote model.

## Setup

This project uses `uv` and `pyproject.toml` for dependency management. You do not need a `requirements.txt` file.

```bash

# 1. Create the environment and install dependencies
uv sync

# 2. Copy the example environment file
copy .env.example .env

# 3. Edit .env and set the model you want to use
#    For local Ollama usage, keep the default values.
#    For a hosted model, update OPENAI_API_KEY, OPENAI_BASE_URL, and CHAT_MODEL.

# 4. Start Ollama if you are using local models
ollama serve

# 5. Pull at least one local model if needed
ollama pull qwen3.5:cloud

# 6. Run the app
uv run python app.py
```

If you already have the environment created, you can jump straight to `uv run python app.py` after updating `.env`.

## Configuration

The application reads these environment variables from `.env`:

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | `ollama` | API key passed to the OpenAI client. The default works for local Ollama usage. |
| `OPENAI_BASE_URL` | `http://localhost:11434/v1` | OpenAI-compatible base URL. Ollama exposes this endpoint locally. |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Base URL used when listing local Ollama models. |
| `CHAT_MODEL` | `qwen3.5:cloud` | Model used for the discovery and recommendation loop. |

For local usage, the simplest `.env` is usually the same as `.env.example`.

## Usage

Run the app, then describe the kind of agentic workflow you are trying to build.

```text
Describe your agentic workflow: I'm building a customer support agent with tool calling

Examples:
1. I'm building a marketing automation agent for campaign creation and report generation.
2. Best LLMs for a customer support agentic workflow with tool calling.
3. Which models are best for a coding assistant agent that runs tests and fixes bugs?

Session History:
1. I'm building a customer support agent with tool calling
```

Available commands inside the CLI:

| Input | Action |
|---|---|
| Any text | Search for LLMs for that workflow |
| `history` or `h` | Show prompts from the current session |
| `quit`, `exit`, or `q` | Exit the program |
| `Ctrl+C` | Exit immediately |

## Output

Each recommendation includes a ranked model list with fields such as:

- model name and provider
- a short description
- parameter family or size
- key features
- tool-calling support
- cost tier
- context window
- suitability score

The app also prints a compact comparison table and any detected local Ollama models.

## Project Structure

```text
agentlens/
├── app.py          # CLI entry point and main loop
├── agent_core.py   # OpenAI-compatible chat loop and web search tool calls
├── ollama_utils.py  # Local Ollama model listing and filtering helpers
├── display.py      # Terminal rendering helpers
├── config.py       # Settings, defaults, and system prompt
├── .env.example    # Environment variable template
├── pyproject.toml  # Dependency and project metadata
└── README.md
```

## Tech Stack

| Component | Technology |
|---|---|
| AI client | OpenAI Python SDK via `chat.completions` |
| Search | DuckDuckGo search through `ddgs` |
| Local model runtime | Ollama REST API |
| Environment config | `python-dotenv` |
| Dependency management | `uv` |

## Troubleshooting

- If the app cannot connect to Ollama, make sure the Ollama server is running and that `OLLAMA_BASE_URL` matches your local endpoint.
- If the recommendation loop fails on a model, try changing `CHAT_MODEL` to another Ollama model you have already pulled.
- If you are using a hosted provider, confirm that the endpoint is OpenAI-compatible and that the API key is valid.
- If `uv run python app.py` fails after editing dependencies, run `uv sync` again to refresh the environment.

## Example `.env`

```env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OLLAMA_BASE_URL=http://localhost:11434
CHAT_MODEL=qwen3.5:cloud
```
