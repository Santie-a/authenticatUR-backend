from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CLIENT_ID: str
    CLIENT_SECRET: str
    TENANT_ID: str
    REDIRECT_URI: str
    AUTHORITY: str
    SCOPE: str
    SESSION_SECRET_KEY: str
    DB_PASSWORD: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    FRONTEND_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
