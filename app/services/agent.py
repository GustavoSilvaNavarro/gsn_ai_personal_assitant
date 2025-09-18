import typer
from typing import List, Optional
from datetime import datetime, timezone
from json import loads, JSONDecodeError

from pydantic import BaseModel, Field, ValidationError

from .notion import create_notion_page
from .recording_capabilities import transformation_audio_to_text
from langgraph.graph import StateGraph, START, END
from .llm import model
from langchain_core.messages import AIMessage
from .prompts import notion_assistant_prompt, notion_user_prompt


# ----------------------------
# Domain Models
# ----------------------------
class NotionPageData(BaseModel):
    title: str = Field(..., description="A concise title for the content.")
    text: List[str] = Field(..., description="A list of all paragraphs for the text.")
    icon: str = Field(..., description="A random emoji or icon related to the topic.")


class AgentState(BaseModel):
    messages: List = Field(default_factory=list)   # holds Human/AI messages
    page_data: Optional[NotionPageData] = None
    error: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ----------------------------
# State Updater Helpers
# ----------------------------
def add_messages(state: AgentState, new_messages: List) -> AgentState:
    return state.model_copy(update={
        "messages": state.messages + new_messages,
        "updated_at": datetime.now(timezone.utc)
    })


def set_page_data(state: AgentState, page_data: NotionPageData) -> AgentState:
    return state.model_copy(update={
        "page_data": page_data,
        "updated_at": datetime.now(timezone.utc)
    })


def set_error(state: AgentState, error_msg: str) -> AgentState:
    return state.model_copy(update={
        "error": error_msg,
        "updated_at": datetime.now(timezone.utc)
    })


# ----------------------------
# LangGraph Nodes
# ----------------------------
def add_system_details(state: AgentState) -> AgentState:
    """
    Adds the system message to the state.
    """
    return add_messages(state, [notion_assistant_prompt])


def get_voice_recording(state: AgentState) -> AgentState:
    """
    Get text from the audio using external transformation function.
    """
    transcribed_text = transformation_audio_to_text()
    user_prompt = notion_user_prompt(user_input=transcribed_text)

    return add_messages(state, [user_prompt])


def call_llm(state: AgentState) -> AgentState:
    """
    Invokes the LLM with the current state's messages and returns the LLM's response.
    """
    response = model.llm.invoke(state.messages)
    return add_messages(state, [response])


def parse_llm_response(state: AgentState) -> AgentState:
    """
    Parse the LLM's JSON response and extract structured NotionPageData.
    """
    messages = state.messages
    if not len(messages):
        return set_error(state, "No messages found in state to parse.")

    ai_response = messages[-1]
    if not isinstance(ai_response, AIMessage):
        return set_error(state, "The last message is not from the AI.")

    try:
        content = ai_response.content
        if content.startswith("```json"):
            json_string = content.split("```json")[1].split("```")[0].strip()
        else:
            json_string = content

        parsed_data = loads(json_string)
        ai_payload = NotionPageData(**parsed_data)
        return set_page_data(state, ai_payload)
    except (JSONDecodeError, IndexError, ValidationError) as err:
        typer.secho(f"Error parsing JSON from LLM: {err}", fg=typer.colors.RED, err=True)
        return set_error(state, "Invalid JSON response from LLM.")


async def upload_new_page_into_notion(state: AgentState) -> AgentState:
    """
    Upload parsed Notion page into the Notion API.
    """
    payload = state.page_data
    if not payload:
        return set_error(state, "🔥 Notion data was not able to get parsed to then being used.")

    await create_notion_page(title=payload.title, paragraphs=payload.text, emoji=payload.icon)
    typer.secho("Notion Page Successfully Uploaded")
    return state


# ----------------------------
# Graph Definition
# ----------------------------
def build_graph():
    """
    Creates and compiles the LangGraph state machine.
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("add_system_details", add_system_details)
    workflow.add_node("get_voice_recording", get_voice_recording)
    workflow.add_node("call_llm", call_llm)
    workflow.add_node("parse_llm_response", parse_llm_response)
    workflow.add_node("upload_new_page_into_notion", upload_new_page_into_notion)

    # Define linear flow
    workflow.add_edge(START, "add_system_details")
    workflow.add_edge("add_system_details", "get_voice_recording")
    workflow.add_edge("get_voice_recording", "call_llm")
    workflow.add_edge("call_llm", "parse_llm_response")
    workflow.add_edge("parse_llm_response", "upload_new_page_into_notion")
    workflow.add_edge("upload_new_page_into_notion", END)

    return workflow.compile()


# ----------------------------
# Entrypoint
# ----------------------------
async def build_graph_and_create_new_code_idea():
    app = build_graph()
    initial_state = AgentState()

    typer.echo("--- Starting async graph execution ---")
    final_state = await app.ainvoke(initial_state)

    if final_state.get('error'):
        typer.secho(f"\n🛑 Process failed with error: {final_state.error}", fg=typer.colors.RED, err=True)
    else:
        typer.secho("\n🎉 Process completed successfully!", fg=typer.colors.GREEN)
