from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        extra="ignore",
    )

    app_env: str = "development"
    # La contraseña de PostgreSQL no se escribe aquí. Llega en DATABASE_URL
    # o, si esa URL no está definida, en POSTGRES_PASSWORD (entorno, .env o Compose).
    postgres_user: str = "ecologistica"
    postgres_password: str = ""
    postgres_host: str = "localhost"
    # 5432 es Postgres en el host o en CI. Compose publica el 5433 en el host.
    postgres_port: int = 5432
    postgres_db: str = "ecologistica"
    database_url: str = ""
    jwt_secret: str = "cambie-esta-clave-en-local"
    jwt_expire_minutes: int = 480
    cors_origins: str = "http://localhost:5173"
    redis_url: str = "redis://localhost:6379/0"
    seed_on_startup: bool = False
    seed_admin_email: str = "admin@distrirapido.example.com"
    seed_admin_password: str = ""
    seed_operador_email: str = "operador@distrirapido.example.com"
    seed_operador_password: str = ""
    seed_gerente_email: str = "gerente@distrirapido.example.com"
    seed_gerente_password: str = ""

    @model_validator(mode="after")
    def resolver_database_url(self) -> Self:
        if self.database_url:
            return self
        if not self.postgres_password:
            raise ValueError(
                "Falta la contraseña de PostgreSQL. Defina DATABASE_URL "
                "o POSTGRES_PASSWORD; no se abre una conexión sin contraseña."
            )
        # URL.create recibe la contraseña como argumento. No hay literal
        # postgresql://... en este archivo, que es lo que marca python:S2115.
        self.database_url = URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        ).render_as_string(hide_password=False)
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [origen.strip() for origen in self.cors_origins.split(",") if origen.strip()]


settings = Settings()
