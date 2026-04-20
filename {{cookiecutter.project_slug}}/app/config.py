from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "{{ cookiecutter.project_name }}"
    VERSION: str = "{{ cookiecutter.version }}"
    DEBUG: bool = False
{%- if cookiecutter.use_postgresql == 'y' %}
    DATABASE_URL: str | None = None
{%- endif %}


settings = Settings()
