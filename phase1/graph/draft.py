from pathlib import Path
from phase1.llm import chat

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "draft.md"


def draft_agent(text: str) -> str:
    """Generate a humanized version of the provided text."""

    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = prompt_template.replace("{text}", text)
    return chat(prompt)