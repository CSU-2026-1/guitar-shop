from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #PostgreSQL
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "product_db"
    jwt_secret_key: str = "SECRETNYI_KOD(T)"
    jwt_algorithm: str = "HS256"
    #Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db_recs: int = 1

    @property
    def celery_broker_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    #сборка URL для Redis
    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()