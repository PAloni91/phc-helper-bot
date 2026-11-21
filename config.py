"""All configuration is read here, from environment variables (or a .env file).

Required variables raise a clear error at startup if they are missing,
so the bot fails fast instead of failing later in the middle of a chat.
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def ensure_env(name: str) -> str:
    """Return the value of a required env var or raise if it is not set."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    openrouter_api_key: str
    model: str
    max_input_chars: int
    max_output_tokens: int
    rate_limit_messages: int
    rate_limit_window_seconds: int


def load_settings() -> Settings:
    return Settings(
        telegram_token=ensure_env("TELEGRAM_BOT_TOKEN"),
        openrouter_api_key=ensure_env("OPENROUTER_API_KEY"),
        model=os.getenv("OPENROUTER_MODEL", "openrouter/auto"),
        max_input_chars=int(os.getenv("MAX_INPUT_CHARS", "500")),
        max_output_tokens=int(os.getenv("MAX_OUTPUT_TOKENS", "400")),
        rate_limit_messages=int(os.getenv("RATE_LIMIT_MESSAGES", "5")),
        rate_limit_window_seconds=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")),
    )
