from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_api_key: str | None = Field(default=None, alias="TELEGRAM_API_KEY")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }
