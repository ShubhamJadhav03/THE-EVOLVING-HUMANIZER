from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

from phase1.graph.draft import draft_agent
from phase1.graph.critic import critic_agent
from phase1.graph.refine import refine_agent


# 1. State definition
class AgentState(TypedDict):
    original_task: str
    current_text: str
    critique: str
    score: int
    iterations: int


# 2. Node: Drafter (first draft OR refinement)
def drafter_node(state: AgentState):
    if state["iterations"] == 0:
        print("✍️  Drafting initial text...")
        result = draft_agent(state["original_task"])
    else:
        print("🔧 Refining text...")
        result = refine_agent(state["current_text"], state["critique"])

    return {
        "current_text": result,
        "iterations": state["iterations"] + 1
    }


# 3. Node: Critic
def critic_node(state: AgentState):
    print("🧐 Critiquing...")
    review = critic_agent(state["current_text"])
    return {
        "score": review.get("score", 0),
        "critique": review.get("critique", "")
    }


# 4. Logic Controller (THE SPEED FIX ⚡)
def should_continue(state: AgentState):
    if state["score"] >= 8:
        return END
    
    # SENIOR DEV FIX: Reduce max loops to 1 for AWS Timeout safety
    # 0 (Draft) -> 1 (Refine) -> Stop.
    # This keeps execution under ~20 seconds.
    if state["iterations"] >= 1:
        print("🛑 Timeout Safety Limit Reached. Stopping.")
        return END
        
    return "drafter"


# 5. Build graph
workflow = StateGraph(AgentState)
workflow.add_node("drafter", drafter_node)
workflow.add_node("critic", critic_node)

workflow.set_entry_point("drafter")
workflow.add_edge("drafter", "critic")

workflow.add_conditional_edges(
    "critic",
    should_continue,
    {
        END: END,
        "drafter": "drafter"
    }
)

app = workflow.compile()


# 6. Entry function used by FastAPI
def rewrite(text: str) -> str:
    inputs = {
        "original_task": text,
        "current_text": "",
        "critique": "",
        "score": 0,
        "iterations": 0
    }

    result = app.invoke(inputs)
    return result["current_text"]