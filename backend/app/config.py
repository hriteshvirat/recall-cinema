from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict

MODULE_BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    BASE_DIR: Path = MODULE_BASE_DIR

    # Google Gemini & Cloud settings
    GOOGLE_CLOUD_PROJECT: str = Field(default="", description="Google Cloud Project ID")
    GOOGLE_CLOUD_LOCATION: str = Field(default="global", description="Vertex AI / Google Cloud location")
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    GEMINI_MODEL: str = Field(default="gemini-2.0-flash", description="Preferred Gemini model for reasoning")
    GEMINI_VISION_MODEL: str = Field(default="gemini-2.0-flash", description="Gemini model for video understanding")
    
    # ClickHouse Cloud settings
    CLICKHOUSE_HOST: str = Field(default="localhost", description="ClickHouse Cloud host (e.g. xxx.clickhouse.cloud)")
    CLICKHOUSE_PORT: int = Field(default=8443, description="ClickHouse port (8443 for HTTPS cloud, 8123 for local HTTP)")
    CLICKHOUSE_USER: str = Field(default="default", description="ClickHouse user")
    CLICKHOUSE_PASSWORD: str = Field(default="", description="ClickHouse password")
    CLICKHOUSE_DATABASE: str = Field(default="recall", description="ClickHouse database")
    CLICKHOUSE_SECURE: bool = Field(default=True, description="Use SSL/TLS for ClickHouse")
    
    # ClickHouse MCP settings
    CLICKHOUSE_MCP_COMMAND: str = Field(default="mcp-clickhouse", description="Executable or command for ClickHouse MCP server")
    
    # Paths & storage
    UPLOAD_DIR: Path = MODULE_BASE_DIR / "uploads"
    SAMPLE_DATA_FILE: Path = MODULE_BASE_DIR / "sample_data" / "kitchen_mystery_events.json"
    SAMPLE_VIDEO_FILE: Path = MODULE_BASE_DIR / "sample_data" / "kitchen_mystery_demo.mp4"
    
    # App config
    APP_NAME: str = "RECALL"
    DEBUG: bool = False

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

