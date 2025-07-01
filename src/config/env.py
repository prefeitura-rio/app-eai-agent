from src.utils.infisical import getenv_or_action
import os

# if file .env exists, load it
if os.path.exists("src/config/.env"):
    import dotenv

    dotenv.load_dotenv(dotenv_path="src/config/.env")


LETTA_API_URL = getenv_or_action("LETTA_API_URL")
LETTA_API_TOKEN = getenv_or_action("LETTA_API_TOKEN")

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

# OPENAI
OPENAI_AZURE_API_KEY = getenv_or_action("OPENAI_AZURE_API_KEY")
OPENAI_API_KEY = getenv_or_action("OPENAI_API_KEY")
OPENAI_URL = getenv_or_action("OPENAI_URL")
GPT_SEARCH_MODEL = getenv_or_action("GPT_SEARCH_MODEL")
