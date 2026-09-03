from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://reservas_app:reservas_app@localhost:5432/reservas_db"

    auth_provider: str = "local"
    jwt_secret: str = "dev-only-secret-do-not-use-in-production"
    jwt_issuer: str = "local-idp"
    jwt_audience: str = "reservas-api"
    jwt_expire_minutes: int = 30

    cognito_region: str = ""
    cognito_user_pool_id: str = ""

    azure_tenant_id: str = ""
    azure_client_id: str = ""

    oauth_client_id: str = "reporting-service"
    oauth_client_secret: str = "dev-only-client-secret"

    rate_limit_max_requests: int = 5
    rate_limit_window_seconds: int = 60

    posthog_project_api_key: str = ""
    posthog_host: str = "https://us.i.posthog.com"


settings = Settings()
