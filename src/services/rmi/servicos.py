"""OAuth2 Client Credentials flow implementation for RMI API authentication"""

import asyncio
import time
from typing import Optional, Dict, Any
import aiohttp
from loguru import logger

from src.config.env import (
    RMI_API_URL,
    RMI_OAUTH_ISSUER,
    RMI_OAUTH_CLIENT_ID,
    RMI_OAUTH_CLIENT_SECRET,
    RMI_OAUTH_SCOPES,
)
import httpx


class ServicesClient:

    def __init__(self, token):
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[float] = None
        self._lock = asyncio.Lock()
        self._client = None
        self.base_url = RMI_API_URL
        self.time_out = httpx.Timeout(30.0, read=30.0)
        self.token = token

    async def get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary"""
        async with self._lock:
            # Check if we have a valid token
            if (
                self._access_token
                and self._token_expiry
                and time.time() < self._token_expiry
            ):
                return self._access_token

            # Get new token
            token_data = await self._request_token()
            if token_data is None or "access_token" not in token_data:
                raise Exception("Failed to obtain OAuth2 access token")

            self._access_token = token_data["access_token"]
            # Set expiry with 5-minute buffer for safety
            self._token_expiry = time.time() + token_data["expires_in"] - 300

            return self._access_token

    async def _request_token(self) -> Dict[str, Any]:
        """Request a new access token using Client Credentials flow"""
        if not all([RMI_OAUTH_ISSUER, RMI_OAUTH_CLIENT_ID, RMI_OAUTH_CLIENT_SECRET]):
            raise ValueError(
                "OAuth2 configuration incomplete. "
                "Please set RMI_OAUTH_ISSUER, RMI_OAUTH_CLIENT_ID, and RMI_OAUTH_CLIENT_SECRET environment variables."
            )

        token_url = f"{RMI_OAUTH_ISSUER}/protocol/openid-connect/token"

        data = {
            "grant_type": "client_credentials",
            "client_id": RMI_OAUTH_CLIENT_ID,
            "client_secret": RMI_OAUTH_CLIENT_SECRET,
            "scope": RMI_OAUTH_SCOPES,
        }
        logger.info(data)
        timeout = aiohttp.ClientTimeout(total=30)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    token_url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(
                            f"OAuth2 token request failed: {response.status} - {error_text}"
                        )
                        raise Exception(
                            f"OAuth2 token request failed: {response.status} - {error_text}"
                        )

                    token_data = await response.json()

                    if "access_token" not in token_data:
                        logger.error(
                            f"OAuth2 response missing access_token: {token_data}"
                        )
                        raise Exception("OAuth2 response missing access_token")

                    logger.info("Successfully obtained OAuth2 access token")
                    return token_data

        except aiohttp.ClientError as e:
            logger.error(f"OAuth2 token request failed: {e}")
            raise Exception(f"OAuth2 token request failed: {e}")

    async def get_client(self) -> httpx.AsyncClient:
        """Get an HTTP client with the Authorization header set"""
        # token = await self.get_access_token()
        # if token is None:
        #     raise Exception("Failed to obtain access token for HTTP client")

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=self.time_out,
        )
        return self._client
