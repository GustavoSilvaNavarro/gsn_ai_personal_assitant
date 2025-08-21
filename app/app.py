import asyncio
from typing import Any
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

NOTION_API_TOKEN = os.getenv("NOTION_API_KEY", "super_secret")
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID", "super_secret_id")
NOTION_URI = os.getenv("NOTION_URL", "https://api.notion.com/v1")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")

HEADERS = {
    "Authorization": "Bearer " + NOTION_API_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION,
}


async def create_new_pages_in_notion(payload: dict[str, Any]):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{NOTION_URI}/pages", headers=HEADERS, json=payload, timeout=5000
        )
        resp.raise_for_status()
        return resp.json()


async def create_new_page(title: str, paragraphs: list[str]):
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

    page = await create_new_pages_in_notion(payload=payload)
    print(page)


if __name__ == "__main__":
    paragraphs = ["First paragraph", "Second paragraph"]
    asyncio.run(create_new_page(title="Test page", paragraphs=paragraphs))
