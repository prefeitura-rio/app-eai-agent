from src.utils.infisical import getenv_or_action
import os

# if file .env exists, load it
if os.path.exists("src/config/.env"):
    import dotenv

    dotenv.load_dotenv(dotenv_path="src/config/.env")


LETTA_API_URL = getenv_or_action("LETTA_API_URL")
LETTA_API_TOKEN = getenv_or_action("LETTA_API_TOKEN")

LETTA_STREAM_TIMEOUT = 300
LETTA_STREAM_RETRY_ATTEMPTS = 3
LETTA_STREAM_RETRY_DELAY = 2.0

EAI_AGENT_URL = getenv_or_action("EAI_AGENT_URL")
EAI_AGENT_TOKEN = getenv_or_action("EAI_AGENT_TOKEN")

LLM_MODEL = getenv_or_action("LLM_MODEL")
EMBEDDING_MODEL = getenv_or_action("EMBEDDING_MODEL")
GEMINI_API_KEY = getenv_or_action("GEMINI_API_KEY")
GEMINI_EVAL_MODEL = getenv_or_action(
    "GEMINI_EVAL_MODEL", default="gemini-2.5-pro-preview-06-05"
)

TYPESENSE_CLIENT_API_URL = getenv_or_action("TYPESENSE_CLIENT_API_URL")
TYPESENSE_CLIENT_API_KEY = getenv_or_action("TYPESENSE_CLIENT_API_KEY")
TYPESENSE_STAGING_BEARER_API_KEY = getenv_or_action("TYPESENSE_STAGING_BEARER_API_KEY")

ISSUE_AGENT_ENABLE_SLEEPTIME = (
    getenv_or_action("ISSUE_AGENT_ENABLE_SLEEPTIME").lower() == "false"
)

PG_URI = getenv_or_action("PG_URI")
# --- Conexão direta (TCP) ao Postgres ---
# Usado quando não queremos depender da SQL Admin API/Connector
DB_SSL = getenv_or_action("DB_SSL", default="true")


PHOENIX_HOST = getenv_or_action("PHOENIX_HOST")
PHOENIX_PORT = getenv_or_action("PHOENIX_PORT")
PHOENIX_ENDPOINT = getenv_or_action("PHOENIX_ENDPOINT")

GCP_SERVICE_ACCOUNT_CREDENTIALS = getenv_or_action(
    "GCP_SERVICE_ACCOUNT_CREDENTIALS", action="raise"
)
GOOGLE_BIGQUERY_PAGE_SIZE = int(
    getenv_or_action("GOOGLE_BIGQUERY_PAGE_SIZE", default="100")
)
NOMINATIM_API_URL = getenv_or_action("NOMINATIM_API_URL")

GOOGLE_MAPS_API_URL = getenv_or_action("GOOGLE_MAPS_API_URL")
GOOGLE_MAPS_API_KEY = getenv_or_action("GOOGLE_MAPS_API_KEY")


# OPENAI
OPENAI_AZURE_API_KEY = getenv_or_action("OPENAI_AZURE_API_KEY")
OPENAI_AZURE_URL = getenv_or_action("OPENAI_AZURE_URL")
OPENAI_AZURE_API_VERSION = getenv_or_action("OPENAI_AZURE_API_VERSION")

OPENAI_API_KEY = getenv_or_action("OPENAI_API_KEY")


GPT_SEARCH_MODEL = getenv_or_action("GPT_SEARCH_MODEL")

EVAL_MODEL_TYPE = getenv_or_action("EVAL_MODEL_TYPE", default="gpt")
GPT_EVAL_MODEL = getenv_or_action("GPT_EVAL_MODEL", default="gpt-4o")

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
CIDADAO_GROUP_NAME = getenv_or_action("CIDADAO_GROUP_NAME", action="ignore")
CIDADAO_API_BASE_URL = getenv_or_action("CIDADAO_API_BASE_URL", action="ignore")
CIDADAO_GOOGLE_SHEET = getenv_or_action("CIDADAO_GOOGLE_SHEET", action="ignore")
