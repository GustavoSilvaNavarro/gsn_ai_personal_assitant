import typer
import asyncio
from typing import Any, List
import httpx
from typing_extensions import Annotated
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment variables and headers configuration
NOTION_API_TOKEN = os.getenv("NOTION_API_KEY", "super_secret")
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID", "super_secret_id")
NOTION_URI = os.getenv("NOTION_URL", "https://api.notion.com/v1")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")

HEADERS = {
    "Authorization": "Bearer " + NOTION_API_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION,
}

# Initialize the Typer application
app = typer.Typer(help="An AI assistant to put your ideas into notion.")


# Async function to create pages in Notion
async def create_new_pages_in_notion(payload: dict[str, Any]):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{NOTION_URI}/pages", headers=HEADERS, json=payload, timeout=5000
        )
        resp.raise_for_status()
        return resp.json()


# Async function to build the page and send the request
async def create_notion_page(title: str, paragraphs: List[str]):
    paragraphs_children = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"text": {"content": text}}]},
        }
        for text in paragraphs
    ]

    payload = {
        "parent": {"page_id": NOTION_PARENT_PAGE_ID},
        "icon": {"type": "emoji", "emoji": "🥳"},
        "properties": {"title": [{"text": {"content": title}}]},
        "children": paragraphs_children,
    }

    try:
        page = await create_new_pages_in_notion(payload=payload)
        typer.echo(f"Successfully created a new Notion page with ID: {page['id']}")
    except httpx.HTTPStatusError as err:
        typer.echo(f"Error creating Notion page: {err.response.text}", err=True)


@app.command(name="new-page")
def cli_add_new_page(
    title: Annotated[
        str,
        typer.Option(
            ...,
            prompt="Enter page title",
            help="The title of the new Notion page.",
        ),
    ],
    paragraphs: Annotated[
        List[str],
        typer.Option(
            ...,
            "--paragraph",
            help="Paragraphs for the page content.",
        ),
    ],
):
    """
    Creates a new page in Notion.
    """
    asyncio.run(create_notion_page(title=title, paragraphs=paragraphs))


@app.command("create")
def cli_create_user(username: str):
    print(f"Creating user: {username}")


if __name__ == "__main__":
    app()
