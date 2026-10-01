from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        extra="ignore",
    )

    app_env: str = "development"
    database_url: str = (
        "postgresql+psycopg://ecologistica:ecologistica@localhost:5432/ecologistica"
    )
    jwt_secret: str = "cambie-esta-clave-en-local"
    jwt_expire_minutes: int = 480
    cors_origins: str = "http://localhost:5173"
    seed_on_startup: bool = False
    seed_admin_email: str = "admin@distrirapido.example.com"
    seed_admin_password: str = ""
    seed_operador_email: str = "operador@distrirapido.example.com"
    seed_operador_password: str = ""
    seed_gerente_email: str = "gerente@distrirapido.example.com"
    seed_gerente_password: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [origen.strip() for origen in self.cors_origins.split(",") if origen.strip()]


settings = Settings()
