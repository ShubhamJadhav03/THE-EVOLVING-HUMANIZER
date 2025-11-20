from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat(prompt):
    res = client.chat.completions.create(
        model="gpt-5-mini",
        messages = [{
                "role": "user",
                "content": prompt
            }]
    )

    content = res.choices[0].message.content

    # token usage log which will be useful for cost tracking in the future

    print("Prompt tokens:", res.usage.prompt_tokens)
    print("Completion tokens:", res.usage.completion_tokens)
    print("Total tokens:", res.usage.total_tokens)

    return content



