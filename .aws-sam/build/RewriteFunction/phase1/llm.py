from functools import lru_cache
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


@lru_cache(maxsize=1)
def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Please add it to your environment or .env file."
        )

    return OpenAI(api_key=api_key)


def chat(prompt: str) -> str:
    client = _get_client()
    res = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    content = res.choices[0].message.content

    # token usage log which will be useful for cost tracking in the future
    print("Prompt tokens:", res.usage.prompt_tokens)
    print("Completion tokens:", res.usage.completion_tokens)
    print("Total tokens:", res.usage.total_tokens)

    return content