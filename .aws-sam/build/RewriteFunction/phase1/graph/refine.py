from pathlib import Path

from phase1.llm import chat

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "refine.md"


def refine_agent(text: str, critique: str) -> str:
    """Refine the humanized text using the provided critique."""

    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = prompt_template.replace("{text}", text).replace("{critique}", critique)

    return chat(prompt)