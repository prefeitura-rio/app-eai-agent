from src.utils.infisical import getenv_or_action

LETTA_API_URL = getenv_or_action("LETTA_API_URL")
LETTA_API_TOKEN = getenv_or_action("LETTA_API_TOKEN")

# CELERY_BROKER_URL = getenv_or_action("CELERY_BROKER_URL")
# CELERY_RESULT_BACKEND = getenv_or_action("CELERY_RESULT_BACKEND")

AGENTIC_SEARCH_API_TOKEN = getenv_or_action("AGENTIC_SEARCH_API_TOKEN")

LLM_MODEL = getenv_or_action("LLM_MODEL")
EMBEDDING_MODEL = getenv_or_action("EMBEDDING_MODEL")

ISSUE_AGENT_ENABLE_SLEEPTIME = getenv_or_action("ISSUE_AGENT_ENABLE_SLEEPTIME").lower() == "false"