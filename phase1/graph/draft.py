from llm import chat

def draft_agent(text: str) ->str:
    """This agent will generate humanise version of text based on original content provided."""

    prompt = open("prompts/draft.md").read().format(text=text)
    return chat(prompt)

    