import typer
from typing import Any, List
import httpx

from app.config import config

HEADERS = {
    "Authorization": "Bearer " + config.NOTION_API_KEY,
    "Content-Type": "application/json",
    "Notion-Version": config.NOTION_VERSION,
}

async def create_new_pages_in_notion(payload: dict[str, Any]):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{config.NOTION_URL}/pages", headers=HEADERS, json=payload, timeout=5000
        )
        resp.raise_for_status()
        return resp.json()


# Async function to build the page and send the request
async def create_notion_page(title: str, paragraphs: List[str], emoji="🥳"):
    paragraphs_children = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"text": {"content": text}}]},
        }
        for text in paragraphs
    ]

    payload = {
        "parent": {"page_id": config.NOTION_PARENT_PAGE_ID},
        "icon": {"type": "emoji", "emoji": emoji},
        "properties": {"title": [{"text": {"content": title}}]},
        "children": paragraphs_children,
    }

    try:
        page = await create_new_pages_in_notion(payload=payload)
        typer.echo(f"Successfully created a new Notion page with ID: {page['id']}")
    except httpx.HTTPStatusError as err:
        typer.echo(f"Error creating Notion page: {err.response.text}", err=True)
