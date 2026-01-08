from src.utils.infisical import getenv_or_action
import os

# if file .env exists, load it
if os.path.exists("src/config/.env"):
    import dotenv

    dotenv.load_dotenv(dotenv_path="src/config/.env", override=True)


INFISICAL_HOST = getenv_or_action("INFISICAL_HOST", action="ignore")
INFISICAL_TOKEN = getenv_or_action("INFISICAL_TOKEN", action="ignore")
INFISICAL_PROJECT_ID = getenv_or_action("INFISICAL_PROJECT_ID", action="ignore")

LETTA_API_URL = getenv_or_action("LETTA_API_URL", action="ignore")
LETTA_API_TOKEN = getenv_or_action("LETTA_API_TOKEN", action="ignore")

LETTA_STREAM_TIMEOUT = 300
LETTA_STREAM_RETRY_ATTEMPTS = 3
LETTA_STREAM_RETRY_DELAY = 2.0

EAI_AGENT_URL = getenv_or_action("EAI_AGENT_URL", action="ignore")
EAI_AGENT_TOKEN = getenv_or_action("EAI_AGENT_TOKEN", action="ignore")

LLM_MODEL = getenv_or_action("LLM_MODEL", action="ignore")
EMBEDDING_MODEL = getenv_or_action("EMBEDDING_MODEL", action="ignore")
GEMINI_API_KEY = getenv_or_action("GEMINI_API_KEY", action="ignore")
GEMINI_EVAL_MODEL = getenv_or_action(
    "GEMINI_EVAL_MODEL", default="gemini-2.5-pro-preview-06-05", action="ignore"
)

TYPESENSE_CLIENT_API_URL = getenv_or_action("TYPESENSE_CLIENT_API_URL", action="ignore")
TYPESENSE_CLIENT_API_KEY = getenv_or_action("TYPESENSE_CLIENT_API_KEY", action="ignore")
TYPESENSE_STAGING_BEARER_API_KEY = getenv_or_action(
    "TYPESENSE_STAGING_BEARER_API_KEY", action="ignore"
)

ISSUE_AGENT_ENABLE_SLEEPTIME = (
    getenv_or_action("ISSUE_AGENT_ENABLE_SLEEPTIME", action="ignore").lower() == "false"
)

PG_URI = getenv_or_action("PG_URI", action="ignore")
# --- Conexão direta (TCP) ao Postgres ---
# Usado quando não queremos depender da SQL Admin API/Connector
DB_SSL = getenv_or_action("DB_SSL", default="true", action="ignore")


PHOENIX_HOST = getenv_or_action("PHOENIX_HOST", action="ignore")
PHOENIX_PORT = getenv_or_action("PHOENIX_PORT", action="ignore")
PHOENIX_ENDPOINT = getenv_or_action("PHOENIX_ENDPOINT", action="ignore")

GCP_SERVICE_ACCOUNT_CREDENTIALS = getenv_or_action(
    "GCP_SERVICE_ACCOUNT_CREDENTIALS", action="raise"
)
GOOGLE_BIGQUERY_PAGE_SIZE = int(
    getenv_or_action("GOOGLE_BIGQUERY_PAGE_SIZE", default="100", action="ignore")
)
NOMINATIM_API_URL = getenv_or_action("NOMINATIM_API_URL", action="ignore")

GOOGLE_MAPS_API_URL = getenv_or_action("GOOGLE_MAPS_API_URL", action="ignore")
GOOGLE_MAPS_API_KEY = getenv_or_action("GOOGLE_MAPS_API_KEY", action="ignore")


# OPENAI
OPENAI_AZURE_API_KEY = getenv_or_action("OPENAI_AZURE_API_KEY", action="ignore")
OPENAI_AZURE_URL = getenv_or_action("OPENAI_AZURE_URL", action="ignore")
OPENAI_AZURE_API_VERSION = getenv_or_action("OPENAI_AZURE_API_VERSION", action="ignore")

OPENAI_API_KEY = getenv_or_action("OPENAI_API_KEY", action="ignore")


GPT_SEARCH_MODEL = getenv_or_action("GPT_SEARCH_MODEL", action="ignore")

EVAL_MODEL_TYPE = getenv_or_action("EVAL_MODEL_TYPE", default="gpt", action="ignore")
GPT_EVAL_MODEL = getenv_or_action("GPT_EVAL_MODEL", default="gpt-4o", action="ignore")

USE_LOCAL_API = (
    getenv_or_action("USE_LOCAL_API", default="false", action="ignore") == "true"
)

EAI_GATEWAY_API_URL = getenv_or_action("EAI_GATEWAY_API_URL")
EAI_GATEWAY_API_TOKEN = getenv_or_action("EAI_GATEWAY_API_TOKEN")

MCP_SERVER_URL = getenv_or_action("MCP_SERVER_URL", action="ignore")
MCP_API_TOKEN = getenv_or_action("MCP_API_TOKEN", action="ignore")


CIDADAO_ISSUER = getenv_or_action("CIDADAO_ISSUER", action="ignore")
CIDADAO_CLIENT_ID = getenv_or_action("CIDADAO_CLIENT_ID", action="ignore")
CIDADAO_CLIENT_SECRET = getenv_or_action("CIDADAO_CLIENT_SECRET", action="ignore")
CIDADAO_API_BASE_URL = getenv_or_action("CIDADAO_API_BASE_URL", action="ignore")


# OAuth2 Configuration for RMI API
RMI_API_URL = getenv_or_action("RMI_API_URL", action="ignore")
RMI_OAUTH_ISSUER = getenv_or_action("RMI_OAUTH_ISSUER", action="ignore")
RMI_OAUTH_CLIENT_ID = getenv_or_action("RMI_OAUTH_CLIENT_ID", action="ignore")
RMI_OAUTH_CLIENT_SECRET = getenv_or_action("RMI_OAUTH_CLIENT_SECRET", action="ignore")
RMI_OAUTH_SCOPES = getenv_or_action(
    "RMI_OAUTH_SCOPES", default="profile email", action="ignore"
)

SERVICOS_CPF = getenv_or_action("SERVICOS_CPF", action="ignore")
SERVICOS_PW = getenv_or_action("SERVICOS_PW", action="ignore")


# Discord Notifications
DISCORD_WEBHOOK_URL = getenv_or_action("DISCORD_WEBHOOK_URL", action="ignore")
DISCORD_THREAD_ID = getenv_or_action("DISCORD_THREAD_ID", action="ignore")
DISCORD_BOT_NAME = getenv_or_action("DISCORD_BOT_NAME", action="ignore")
DISCORD_BOT_AVATAR_URL = getenv_or_action("DISCORD_BOT_AVATAR_URL", action="ignore")
DISCORD_ENABLE_DEV_TESTING = (
    getenv_or_action(
        "DISCORD_ENABLE_DEV_TESTING", default="false", action="ignore"
    ).lower()
    == "true"
)
ENVIRONMENT = getenv_or_action("ENVIRONMENT", default="development", action="ignore")

# Beta Group / Whitelist Configuration
WHITELIST_API_BASE_URL_STAGING = getenv_or_action(
    "WHITELIST_API_BASE_URL_STAGING", action="ignore"
)
WHITELIST_ISSUER_STAGING = getenv_or_action("WHITELIST_ISSUER_STAGING", action="ignore")
WHITELIST_CLIENT_ID_STAGING = getenv_or_action(
    "WHITELIST_CLIENT_ID_STAGING", action="ignore"
)
WHITELIST_CLIENT_SECRET_STAGING = getenv_or_action(
    "WHITELIST_CLIENT_SECRET_STAGING", action="ignore"
)

WHITELIST_API_BASE_URL_PROD = getenv_or_action(
    "WHITELIST_API_BASE_URL_PROD", action="ignore"
)
WHITELIST_ISSUER_PROD = getenv_or_action("WHITELIST_ISSUER_PROD", action="ignore")
WHITELIST_CLIENT_ID_PROD = getenv_or_action("WHITELIST_CLIENT_ID_PROD", action="ignore")
WHITELIST_CLIENT_SECRET_PROD = getenv_or_action(
    "WHITELIST_CLIENT_SECRET_PROD", action="ignore"
)

WHITELIST_GOOGLE_SHEET = getenv_or_action("WHITELIST_GOOGLE_SHEET", action="ignore")
