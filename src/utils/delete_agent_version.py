import requests
from src.config import env

url = f"{env.EAI_AGENT_URL_PROD}api/v1/unified-delete"

headers = {"Authorization": f"Bearer {env.EAI_AGENT_TOKEN_PROD}"}

params = {
    "version_number": 12, # integer
    "agent_type": "agentic_search"
}

response = requests.delete(url, headers=headers, params=params)

print(response.text)