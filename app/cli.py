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
def cli_create_user(
    username: str = typer.Option(
        ...,
        "--username",
        "-u",
        help="The username for the new user."
    )
):
    print(f"Creating user: {username}")

@app.command("mmm")
def cli_get_mmm(
    topic: str = typer.Option(
        ...,
        "--topic", "-t", help="Topic required to get the MMM"
    )
):
    """
    MMM => Monday Morning Mediation.

    It creates a new MMM phrase, related to the topic you sent.
    """
    print(f"MMM => Buddha says.... => {topic}")


def main():
    app()

if __name__ == "__main__":
    main()
