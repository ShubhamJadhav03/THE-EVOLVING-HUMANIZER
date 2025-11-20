from llm import chat

def refine_agent(text: str, critique: str) -> str:
    """This agent will refine the humanised text based on the critique provided."""

    prompt = open("prompts/refine.md").read().format(
        text=text,
        critique=critique
    )
    
    return chat(prompt)