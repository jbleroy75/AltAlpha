from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/altalpha.db"
    sec_user_agent: str = "AltAlpha/0.8 github.com/jbleroy75/AltAlpha"
    lda_api_key: str | None = None
    uspto_api_key: str | None = None
    google_trends_api_url: str | None = None
    google_trends_api_key: str | None = None
    bluesky_base_url: str = "https://public.api.bsky.app"
    watchlist: str = "AAPL,MSFT,NVDA,AMZN,META,GOOGL,TSLA,PLTR,JPM,GS"
    auto_sync_on_first_run: bool = True
    bootstrap_price_years: int = 5
    congress_public_api_url: str = "https://www.bargo.ai/free-apis/congress/v1"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
