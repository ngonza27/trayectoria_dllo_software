from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Slide 16 — "Manejo Seguro de Credenciales": every value here is read from
    the environment (.env locally, real secret storage in production), never
    hardcoded. See .env.example for the full list and docs/security-architecture.md
    for how AUTH_PROVIDER swaps this app's own JWTs for real Cognito/Azure AD tokens.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://reservas_app:reservas_app@localhost:5432/reservas_db"

    auth_provider: str = "local"  # "local" | "cognito" | "azure"
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

    # PostHog product analytics + session replay (slide 8/11). The project
    # API key is meant to be public — it's what posthog-js embeds client-side
    # — so it is safe to serve from GET /public-config. The personal API key
    # is a SECRET, read-only credential used only server-side (app/analytics.py)
    # to list session recordings for manual verification; it must never be
    # sent to the browser or committed to source control.
    posthog_project_api_key: str = ""
    posthog_personal_api_key: str = ""
    posthog_host: str = "https://us.i.posthog.com"


settings = Settings()
