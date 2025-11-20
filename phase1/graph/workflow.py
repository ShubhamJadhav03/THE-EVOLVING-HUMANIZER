from graph.draft import draft_agent
from graph.critic import critic_agent
from graph.refine import refine_agent

def rewrite(text: str) -> str:
    """This function will orchestrate the drafting, critiquing, and refining of the provided text."""
    
    draft = draft_agent(text)

    for _ in range(3):  # Iterate the critique and refine process 3 times
        review = critic_agent(draft)

        if review["score"] >= 8:
            return draft  # If score is satisfactory, return the draft
        
        draft = refine_agent(draft, review["critique"])
    
    return draft  # Return the final draft after all iterations