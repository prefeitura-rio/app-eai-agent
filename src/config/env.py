from src.utils.infisical import getenv_or_action

LETTA_API_URL = getenv_or_action("LETTA_API_URL")
LETTA_API_TOKEN = getenv_or_action("LETTA_API_TOKEN")

EAI_AGENT_URL = getenv_or_action("EAI_AGENT_URL")
EAI_AGENT_TOKEN = getenv_or_action("EAI_AGENT_TOKEN")

LLM_MODEL = getenv_or_action("LLM_MODEL")
EMBEDDING_MODEL = getenv_or_action("EMBEDDING_MODEL")
GEMINI_API_KEY = getenv_or_action("GEMINI_API_KEY")

TYPESENSE_CLIENT_API_URL = getenv_or_action("TYPESENSE_CLIENT_API_URL")
TYPESENSE_CLIENT_API_KEY = getenv_or_action("TYPESENSE_CLIENT_API_KEY")
TYPESENSE_STAGING_BEARER_API_KEY = getenv_or_action("TYPESENSE_STAGING_BEARER_API_KEY")

ISSUE_AGENT_ENABLE_SLEEPTIME = (
    getenv_or_action("ISSUE_AGENT_ENABLE_SLEEPTIME").lower() == "false"
)

PG_URI = getenv_or_action("PG_URI")
