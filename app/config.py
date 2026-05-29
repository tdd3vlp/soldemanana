from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str
    admin_ids_raw: str = Field(default="", alias="admin_ids")

    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    openai_fast_model: str = "gpt-4o-mini"
    openai_strong_model: str = "gpt-4o"
    openai_summary_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 450
    openai_correction_max_tokens: int = 650
    openai_summary_max_tokens: int = 160
    openai_temperature: float = 0.7
    dialog_history_size: int = 4
    dialog_message_char_limit: int = 500
    memory_summary_interval: int = 12
    memory_summary_char_limit: int = 700
    ai_input_cost_per_1m: float = 0.15
    ai_output_cost_per_1m: float = 0.60

    database_url: str
    db_pool_size: int = 10
    db_max_overflow: int = 20

    redis_url: str = "redis://localhost:6379/0"

    webhook_enabled: bool = False
    webhook_url: str = ""
    webhook_path: str = "/webhook/bot"
    webhook_secret: str = ""

    web_app_base_url: str = ""
    subscription_web_app_path: str = "/subscription"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    log_level: str = "INFO"
    environment: str = "development"

    yookassa_shop_id: str = ""
    yookassa_secret_key: str = ""

    @computed_field
    @property
    def admin_ids(self) -> list[int]:
        if not self.admin_ids_raw:
            return []
        v = self.admin_ids_raw.strip()
        if v.startswith('[') and v.endswith(']'):
            import json
            return json.loads(v)
        return [int(x.strip()) for x in v.split(",") if x.strip()]

    @computed_field
    @property
    def subscription_web_app_url(self) -> str:
        base_url = self.web_app_base_url or self.webhook_url
        if not base_url:
            return ""
        return f"{base_url.rstrip('/')}{self.subscription_web_app_path}"


settings = Settings()
