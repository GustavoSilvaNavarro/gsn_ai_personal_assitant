from pydantic import BaseModel, Field
from typing import List


class QuoteMMM(BaseModel):
    author: str
    phrase: str


class NotionPageData(BaseModel):
    title: str = Field(..., description="A concise title for the content.")
    text: List[str] = Field(..., description="A list of all paragraphs for the text.")
    icon: str = Field(..., description="A random emoji or icon related to the topic.")
