from typing import Annotated, List, Optional

from typing_extensions import TypedDict
from .recording_capabilities import transformation_audio_to_text
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# from langgraph.graph.state import CompiledStateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage
from json import loads, JSONDecodeError
from .prompts import notion_assistant_prompt, notion_user_prompt
from app.config import config
from pydantic import BaseModel, Field


llm = ChatGoogleGenerativeAI(
    google_api_key=config.AI_API_KEY,
    model=config.AI_MODEL,
    temperature=0,
)


# Define the data structure for the parsed LLM response
class NotionPageData(BaseModel):
    title: str = Field(..., description="A concise title for the content.")
    text: List[str] = Field(..., description="A list of all paragraphs for the text.")
    icon: str = Field(..., description="A random emoji or icon related to the topic.")


class AgentState(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]
    page_data: Optional[NotionPageData]


def get_voice_recording(state: AgentState):
    """
    LangGraph node to get text from the audio.
    It directly calls the external function `transformation_audio_to_text`.
    """
    transcribed_text = transformation_audio_to_text()
    user_prompt = notion_user_prompt(user_input=transcribed_text)

    # Return the transcribed text as a HumanMessage
    return {"messages": [notion_assistant_prompt, user_prompt]}


def call_llm(state: AgentState):
    """
    Invokes the LLM with the current state's messages and returns the LLM's response.
    """
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


def parse_llm_response(state: AgentState):
    """
    LangGraph node to parse the LLM's JSON response and extract specific data.
    """
    messages = state.get("messages", [])
    if not messages:
        raise ValueError("No messages found in state to parse.")

    ai_response = messages[-1]

    if not isinstance(ai_response, AIMessage):
        raise TypeError("The last message is not from the AI.")

    try:
        # Get the content from the AI response
        content = ai_response.content

        # Strip the markdown code block markers if they are present
        if content.startswith("```json"):
            # This is a safe way to extract the content between the markers
            json_string = content.split("```json")[1].split("```")[0].strip()
        else:
            json_string = content

        # Load the cleaned JSON string
        parsed_data = loads(json_string)
        ai_payload = NotionPageData(**parsed_data)

        return {"page_data": ai_payload}
    except (JSONDecodeError, IndexError) as err:
        print(f"Error parsing JSON from LLM: {err}")
        return {"error": "Invalid JSON response from LLM."}


def build_graph():
    """
    Creates and compiles the LangGraph state machine.
    This is the core logic of our agent.
    """
    workflow = StateGraph(AgentState)

    # Add the nodes to the graph
    workflow.add_node("get_voice_recording", get_voice_recording)
    workflow.add_node("call_llm", call_llm)
    workflow.add_node("parse_llm_response", parse_llm_response)

    # Define Linear flow (edges)
    workflow.add_edge(START, "get_voice_recording")
    workflow.add_edge("get_voice_recording", "call_llm")
    workflow.add_edge("call_llm", "parse_llm_response")
    workflow.add_edge("parse_llm_response", END)

    return workflow.compile()


if __name__ == "__main__":
    app = build_graph()

    # Invoke the graph with an initial state
    initial_state = {"messages": []}
    final_state = app.invoke(initial_state)

    print("--- Final State of the Graph ---")
    print(final_state)
