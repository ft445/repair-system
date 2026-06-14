from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./repair_system.db"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    UPLOAD_DIR: str = "./uploads"
    PG_POOL_SIZE: int = 20        # 最小连接数
    PG_MAX_OVERFLOW: int = 40     # 最大额外连接数（突发流量）

    class Config:
        env_file = ".env"


settings = Settings()
