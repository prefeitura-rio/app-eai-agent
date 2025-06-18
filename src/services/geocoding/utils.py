import base64
import json
import datetime

import requests
from google.cloud import bigquery
from google.oauth2 import service_account
from typing import List
from src.config import env as config
import src.services.geocoding.openlocationcode as olc
from loguru import logger


class CustomJSONEncoder(json.JSONEncoder):
    """
    JSON Encoder customizado que sabe como converter objetos
    de data, hora e data/hora do Python para strings no padrão ISO 8601.
    """

    def default(self, obj):
        # Se o objeto for uma instância de datetime, date ou time...
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            # ... converta-o para uma string no formato ISO.
            return obj.isoformat()

        # Para qualquer outro tipo, deixe o encoder padrão fazer o trabalho.
        return super().default(obj)


def geocode_address_to_plus8(address):
    params = {"q": address, "format": "json", "addressdetails": 1, "limit": 1}
    headers = {
        "User-Agent": "YourAppName/1.0 (your.email@example.com)"  # Required by Nominatim
    }
    response = requests.get(config.NOMINATIM_API_URL, params=params, headers=headers)
    response.raise_for_status()
    logger.info(f"Geocoding adress: {address}")
    data = response.json()
    if data:
        coords = {
            "lat": float(data[0]["lat"]),
            "lon": float(data[0]["lon"]),
            "display_name": data[0]["display_name"],
        }

        coords_info = json.dumps(coords, ensure_ascii=False, indent=2)
        logger.info(f"\nGeolocated info:\n {coords_info}")
        plus8 = olc.encode(
            latitude=coords["lat"], longitude=coords["lon"], codeLength=8
        )
        logger.info(f"Encoded plus8 {plus8}")
        return plus8

    else:
        return None


def get_bigquery_client() -> bigquery.Client:
    """Get the BigQuery client.

    Returns:
        bigquery.Client: The BigQuery client.
    """
    credentials = get_gcp_credentials(
        scopes=[
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/cloud-platform",
        ]
    )
    return bigquery.Client(credentials=credentials, project=credentials.project_id)


def get_gcp_credentials(scopes: List[str] = None) -> service_account.Credentials:
    """Get the GCP credentials.

    Args:
        scopes (List[str], optional): The scopes to use. Defaults to None.

    Returns:
        service_account.Credentials: The GCP credentials.
    """
    info: dict = json.loads(base64.b64decode(config.GCP_SERVICE_ACCOUNT_CREDENTIALS))
    creds = service_account.Credentials.from_service_account_info(info)
    if scopes:
        creds = creds.with_scopes(scopes)
    return creds
