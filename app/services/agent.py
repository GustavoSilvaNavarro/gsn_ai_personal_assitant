from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]
    transcribed_text: str
    llm_response: str


def get_transcribed_text(state: AgentState):
    """
    A node to get the transcribed text from the initial state.
    """
    print("Agent is processing the provided text...")
    transcribed_text = state['transcribed_text']
    return {"transcribed_text": transcribed_text}


def call_llm(state: AgentState):
    """
    A node to call the LLM and get a summary.
    This is where your AI model API call would go.
    """
    print("Agent is calling the LLM to get a professional summary...")
    transcribed_text = state['transcribed_text']

    # Placeholder for the LLM response
    # In a real app, you would format a prompt and send it to your model.
    llm_response = f"Summary of the audio: The user recorded a note about '{transcribed_text[:40]}...'."

    print("LLM response received.")
    return {"llm_response": llm_response}


def write_to_notion(state: AgentState):
    """
    A node to write the LLM's response to Notion.
    This is where your Notion API integration would live.
    """
    print("Agent is writing the summary to Notion...")
    llm_response = state['llm_response']

    # Placeholder for Notion API call
    # You would use a library like `notion-client` here.
    # For now, we'll just print the output.
    print(f"Successfully wrote the following summary to Notion:\n\n{llm_response}")
    return {}

def build_graph():
    """
    Creates and compiles the LangGraph state machine.
    This is the core logic of our agent.
    """
    workflow = StateGraph(AgentState)

    # Add the nodes to the graph
    workflow.add_node("get_text", get_transcribed_text)
    workflow.add_node("call_llm", call_llm)
    workflow.add_node("write_to_notion", write_to_notion)

    # Define the linear flow (edges)
    workflow.add_edge(START, "get_text")
    workflow.add_edge("get_text", "call_llm")
    workflow.add_edge("call_llm", "write_to_notion")
    workflow.add_edge("write_to_notion", END)

    return workflow.compile()
