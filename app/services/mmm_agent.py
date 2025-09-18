from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END
from .llm import model
from app.schemas import QuoteMMM
import typer
from .prompts import mmm_system_prompt, mmm_user_prompt_topic


class MMMAgentState(TypedDict):
    messages: Annotated[list, add_messages]  # holds Human/AI messages
    mmm: Optional[dict]
    topic: str


def add_context_to_llm(state: MMMAgentState):
    return {"messages": [mmm_system_prompt]}


def get_topic_from_user(state: MMMAgentState):
    prompt = mmm_user_prompt_topic(topic=state["topic"])
    return {"messages": [prompt]}


def call_llm(state: MMMAgentState):
    response: QuoteMMM = model.llm.invoke(state["messages"])
    ai_response = AIMessage(
        content=f"Author: {response.author} | Phrase: {response.phrase}"
    )
    return {
        "messages": [ai_response],  # keep it in messages if you want history
        "mmm": response.model_dump(),
    }


def build_mmm_graph():
    """
    Creates and compiles the LangGraph state machine.
    """
    workflow = StateGraph(MMMAgentState)

    workflow.add_node("add_context_to_llm", add_context_to_llm)
    workflow.add_node("get_topic_from_user", get_topic_from_user)
    workflow.add_node("call_llm", call_llm)

    workflow.add_edge(START, "add_context_to_llm")
    workflow.add_edge("add_context_to_llm", "get_topic_from_user")
    workflow.add_edge("get_topic_from_user", "call_llm")
    workflow.add_edge("call_llm", END)

    return workflow.compile()


async def run_mmm_graph_agent(topic: str):
    app = build_mmm_graph()
    initial_state = MMMAgentState(messages=[], topic=topic)

    try:
        final_state = await app.ainvoke(initial_state)
        typer.secho(
            f"🎊 Your MMM => {final_state['mmm']['phrase']} | Author: {final_state['mmm']['author']}",
            fg=typer.colors.GREEN,
        )
    except Exception as err:
        typer.secho(f"❌ An error occurred: {err}", fg=typer.colors.RED, err=True)
