from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import config
from app.schemas import QuoteMMM


class LLM:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=config.AI_API_KEY, model=config.AI_MODEL, temperature=0
        )
        self.mmm_structure_llm = self.llm.with_structured_output(QuoteMMM)


model = LLM()
