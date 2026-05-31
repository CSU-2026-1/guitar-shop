from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "orders_db"
    jwt_secret_key: str = "SECRETNYI_KOD(T)"
    jwt_algorithm: str = "HS256"
    kafka_bootstrap_servers: str = "localhost:9092"

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def db_replica_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@postgres-replica:5432/{self.db_name}"

    @property
    def bootstrap_servers(self) -> str:
        return self.kafka_bootstrap_servers

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()