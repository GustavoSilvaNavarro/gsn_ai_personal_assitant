from typing import Annotated

from typing_extensions import TypedDict
from .recording_capabilities import transformation_audio_to_text
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from .prompts import notion_assistant_prompt, notion_user_prompt
from app.config import config


llm = ChatGoogleGenerativeAI(
    google_api_key=config.AI_API_KEY,
    model=config.AI_MODEL,
    temperature=0,
)


class AgentState(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


def get_voice_recording(state: AgentState):
    """
    LangGraph node to get text from the audio.
    It directly calls the external function `transformation_audio_to_text`.
    """
    transcribed_text = transformation_audio_to_text()

    # Return the transcribed text as a HumanMessage
    return {"messages": [HumanMessage(content=transcribed_text)]}



def format_notion_prompt(state: AgentState):
    """
    LangGraph node to format the LLM prompt for Notion.
    It combines the transcribed text with a specific user prompt.
    """
    # Get the transcribed text from the state
    messages = state.get('messages', [])
    if not messages:
        raise ValueError("No messages found in state to format.")

    # The transcribed text is the last message added by get_voice_recording_node
    print(messages)
    transcribed_text = messages[-1].content

    user_prompt = notion_user_prompt(user_input=transcribed_text)

    # Return the combined messages
    return {"messages": [notion_assistant_prompt, user_prompt]}


def call_llm(state: AgentState):
    """
    Invokes the LLM with the current state's messages and returns the LLM's response.
    """
    messages = state['messages']
    response = llm.invoke(messages)
    return {'messages': [response]}


def build_graph():
    """
    Creates and compiles the LangGraph state machine.
    This is the core logic of our agent.
    """
    workflow = StateGraph(AgentState)

    # Add the nodes to the graph
    workflow.add_node("get_voice_recording", get_voice_recording)
    workflow.add_node("format_notion_prompt", format_notion_prompt)
    workflow.add_node("call_llm", call_llm)

    # Define Linear flow (edges)
    workflow.add_edge(START, "get_voice_recording")
    workflow.add_edge("get_voice_recording", "format_notion_prompt")
    workflow.add_edge("format_notion_prompt", "call_llm")
    workflow.add_edge("call_llm", END)

    return workflow.compile()


# TODO: I might need to delate this
def stream_graph_updates(graph: CompiledStateGraph[AgentState, None, AgentState, AgentState], user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        graph = build_graph()
        stream_graph_updates(graph, user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
