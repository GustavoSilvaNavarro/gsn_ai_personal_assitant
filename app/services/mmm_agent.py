from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from .agent import llm
from .prompts import mmm_system_prompt, mmm_user_prompt_topic


class MMMAgentState(TypedDict):
    messages: Annotated[list, add_messages]  # holds Human/AI messages
    topic: str


def add_context_to_llm(state: MMMAgentState):
    return {"messages": [mmm_system_prompt]}


def get_topic_from_user(state: MMMAgentState):
    prompt = mmm_user_prompt_topic(topic=state["topic"])
    return {"messages": [prompt]}


def call_llm(state: MMMAgentState):
    return {"messages": [llm.invoke(state["messages"])]}


def parse_llm_response(state: MMMAgentState):
    msgs = state["messages"]
    print(msgs[-1])


def build_mmm_graph():
    """
    Creates and compiles the LangGraph state machine.
    """
    workflow = StateGraph(MMMAgentState)

    workflow.add_node("add_context_to_llm", add_context_to_llm)
    workflow.add_node("get_topic_from_user", get_topic_from_user)
    workflow.add_node("call_llm", call_llm)
    workflow.add_node("parse_llm_response", parse_llm_response)

    workflow.add_edge(START, "add_context_to_llm")
    workflow.add_edge("add_context_to_llm", "get_topic_from_user")
    workflow.add_edge("get_topic_from_user", "call_llm")
    workflow.add_edge("call_llm", "parse_llm_response")
    workflow.add_edge("parse_llm_response", END)

    return workflow.compile()


async def run_mmm_graph_agent(topic: str):
    app = build_mmm_graph()
    initial_state = MMMAgentState(messages=[], topic=topic)

    final_state = await app.ainvoke(initial_state)
    print(final_state)
