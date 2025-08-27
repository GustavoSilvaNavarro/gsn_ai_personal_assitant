from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Main setup for the backend service."""

    # APP SETTINGS
    ENVIRONMENT: str = Field(description="Environment type", default="dev")

    # ADAPTERS
    SERVICE_NAME: str = Field(description="Service name for the server", default="Notion AI Assistant")
    LOG_LEVEL: str = Field(
        description="Python logging level. Must be a string like 'DEBUG' or 'ERROR'.",
        default="INFO",
    )

    # NOTION
    NOTION_API_KEY: str = Field(description="Notion Key", default="super_secret")
    NOTION_PARENT_PAGE_ID: str = Field(description="Notion Page ID", default="super_secret_id")
    NOTION_URL: str = Field(description="Notion URL", default="https://api.notion.com/v1")
    NOTION_VERSION: str = Field(description="Notion Version", default="2022-06-28")

    # ELEVEN LABS
    ELEVEN_LABS_API_KEY: str = Field(description="API key for eleven labs", default="")
    ELEVEN_LABS_MODEL: str = Field(description="Elevenlabs for audio AI", default="")

    class Config:
        """Override env file, used in dev."""

        env_file = ".env"


config = Config()
