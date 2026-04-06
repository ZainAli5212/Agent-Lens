"""
AgentLens — Ollama Local Model Utilities
"""
import requests
from config import OLLAMA_BASE_URL


def get_local_models() -> list[dict]:
    """
    Fetch all locally installed Ollama models with metadata.
    Returns a list of dicts with name, size, parameter_size, quantization, family.
    """
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        models = resp.json().get("models", [])

        parsed = []
        for m in models:
            details = m.get("details", {})
            parsed.append({
                "name":            m.get("name", "unknown"),
                "size_gb":         round(m.get("size", 0) / 1e9, 2),
                "parameter_size":  details.get("parameter_size", "N/A"),
                "quantization":    details.get("quantization_level", "N/A"),
                "family":          details.get("family", "N/A"),
            })

        return parsed

    except requests.exceptions.ConnectionError:
        return []
    except Exception as e:
        print(f"[ollama] Warning: could not fetch models — {e}")
        return []


def is_ollama_running() -> bool:
    """Quick health-check for the Ollama server."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


def filter_agentic_models(local_models: list[dict]) -> list[dict]:
    """
    Heuristic filter: flag local models that are likely suitable for agentic
    workflows based on their family or name keywords.
    """
    agentic_keywords = {
        "llama", "mistral", "qwen", "gemma", "phi",
        "deepseek", "command", "mixtral", "hermes",
    }
    result = []
    for m in local_models:
        name_lower  = m["name"].lower()
        family_lower = m["family"].lower()
        suitable = any(kw in name_lower or kw in family_lower for kw in agentic_keywords)
        result.append({**m, "agentic_suitable": suitable})
    return result
