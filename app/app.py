import typer
import asyncio
from .services import build_graph_and_create_new_code_idea

# Initialize the Typer application
app = typer.Typer(help="An AI assistant to put your ideas into notion.")

@app.command(name="record-idea")
def cli_record_code_idea():
    """
    Creates a new page in Notion.
    """
    asyncio.run(build_graph_and_create_new_code_idea())


@app.command("create")
def cli_create_user(username: str):
    print(f"Creating user: {username}")


if __name__ == "__main__":
    app()
