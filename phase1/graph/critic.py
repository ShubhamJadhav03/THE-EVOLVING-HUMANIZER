import json
from pathlib import Path
from phase1.llm import chat

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "critic.md"

def critic_agent(text: str) -> dict:
    """Critique the humanized text and return a JSON-like report."""

    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = prompt_template.replace("{text}", text)

    response = chat(prompt)


    clean_response = (
        response.replace("```json", "")
                .replace("```", "")
                .strip()
    )

    try:
        parsed = json.loads(clean_response)
        if "score" in parsed and "critique" in parsed:
            return parsed
    except json.JSONDecodeError:
        pass

    # Fallback – only used rarely
    fix_prompt = f"""
    The following response was not valid JSON.
    Rewrite it as valid JSON with keys "score" and "critique".

    Response:
    {response}
    """

    retry = chat(fix_prompt)
    clean_retry = retry.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(clean_retry)
        return parsed
    except:
        return {"score": 5, "critique": "Model returned invalid JSON."}
