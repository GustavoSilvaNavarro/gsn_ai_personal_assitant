from pydantic import BaseModel

class QuoteMMM(BaseModel):
    author: str
    phrase: str
