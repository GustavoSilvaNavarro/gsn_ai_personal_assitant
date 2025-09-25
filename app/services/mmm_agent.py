from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END
from .llm import model
from langchain_core.messages import HumanMessage
from app.schemas import QuoteMMM
import typer
from .prompts import mmm_system_prompt, mmm_user_prompt_topic


class MMMAgentState(TypedDict):
    messages: Annotated[list, add_messages]  # holds Human/AI messages
    mmm: Optional[dict]
    topic: str
    rejected_quotes: list[str]
    accepted: bool


def add_context_to_llm(state: MMMAgentState):
    return {"messages": [mmm_system_prompt]}


def get_topic_from_user(state: MMMAgentState):
    prompt = mmm_user_prompt_topic(topic=state["topic"])
    return {"messages": [prompt]}


def call_llm(state: MMMAgentState):
    # Build rejection context if user has rejected previous phrases
    rejection_context = ""
    if state["rejected_quotes"]:
        rejection_context = (
            "\nIMPORTANT: Do NOT repeat any of these phrases:\n"
            + "\n".join(f"- {r}" for r in state["rejected_quotes"])
        )

    last_msg = state["messages"][-1]

    if rejection_context:
        prompt = HumanMessage(content=f"{rejection_context}\n\n{last_msg.content}")
    else:
        prompt = HumanMessage(content=last_msg.content)

    print(prompt.content)

    # Run the LLM
    response: QuoteMMM = model.mmm_structure_llm.invoke(
        [*state["messages"][:-1], prompt]
    )

    return {"mmm": response.model_dump()}


def get_user_feedback(state: MMMAgentState):
    phrase = state["mmm"]["phrase"]
    author = state["mmm"]["author"]

    typer.secho(
        f'\n🎊 Your MMM => "{phrase}" — {author}\n',
        fg=typer.colors.GREEN,
    )

    answer = typer.prompt("Do you like this one? (y/n)").strip().lower()

    if answer not in ["y", "n"]:
        typer.secho("❌ Please answer with 'y' or 'n' only.", fg=typer.colors.RED)
        raise typer.Exit(code=1)  # hard exit on invalid input

    if answer == "y":
        typer.secho("✅ Awesome! We'll keep this one.", fg=typer.colors.CYAN)
        ai_response = AIMessage(content=f"Author: {author} | Phrase: {phrase}")
        return {"accepted": True, "messages": [ai_response]}
    else:
        typer.secho("🔄 Okay, generating another one...\n", fg=typer.colors.YELLOW)
        return {
            "accepted": False,
            "rejected_quotes": state["rejected_quotes"] + [phrase],
        }


def build_mmm_graph():
    """
    Creates and compiles the LangGraph state machine.
    """
    workflow = StateGraph(MMMAgentState)

    workflow.add_node("add_context_to_llm", add_context_to_llm)
    workflow.add_node("get_topic_from_user", get_topic_from_user)
    workflow.add_node("call_llm", call_llm)
    workflow.add_node("get_user_feedback", get_user_feedback)

    workflow.add_edge(START, "add_context_to_llm")
    workflow.add_edge("add_context_to_llm", "get_topic_from_user")
    workflow.add_edge("get_topic_from_user", "call_llm")
    workflow.add_edge("call_llm", "get_user_feedback")

    workflow.add_conditional_edges(
        "get_user_feedback",
        lambda state: "end" if state.get("accepted") else "retry",
        {"end": END, "retry": "call_llm"},
    )

    return workflow.compile()


async def run_mmm_graph_agent(topic: str):
    app = build_mmm_graph()
    initial_state = MMMAgentState(
        messages=[], topic=topic, rejected_quotes=[], accepted=False
    )

    try:
        await app.ainvoke(initial_state)
    except typer.Exit:
        pass
    except Exception as err:
        typer.secho(f"❌ An error occurred: {err}", fg=typer.colors.RED, err=True)
