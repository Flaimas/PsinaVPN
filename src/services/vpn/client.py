import json
from typing import Any

import httpx
from httpx import AsyncClient, Response
from loguru import logger

from src.core.config import settings

from .exceptions import (
    RemnawaveConnectionError,
    RemnawaveNotFoundError,
    RemnawaveServerError,
    RemnawaveUnexpectedStatusError,
    RemnawaveValidationError,
)
from .models import (
    RemnawaveCreateUserRequest,
    RemnawaveUserResponse,
)


class RemnawaveClient:
    def __init__(self) -> None:
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.REMNAWAVE_API_TOKEN}",
        }
        self.base_url = settings.REMNAWAVE_BASE_URL
        self._client: AsyncClient | None = None

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def open(self) -> None:
        if self._client is None:
            self._client = AsyncClient(
                headers=self.headers, base_url=self.base_url, trust_env=False
            )

    async def _send_request(
        self,
        method: str,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Response:
        if self._client is None:
            raise RuntimeError(
                "RemnawaveClient не инициализирован — вызови open() перед использованием"
            )

        try:
            response = await self._client.request(
                method=method, url=endpoint, json=json_data, params=params
            )
        except httpx.TimeoutException as e:
            logger.error("Remnawave API timeout | URL: {}", endpoint)
            raise RemnawaveConnectionError("Panel request timed out") from e
        except httpx.ConnectError as e:
            logger.error("Remnawave API connection failed | URL: {}", endpoint)
            raise RemnawaveConnectionError("Cannot connect to panel") from e
        except httpx.HTTPError as e:
            logger.error(
                "Remnawave API unexpected transport error | URL: {} | {}", endpoint, e
            )
            raise RemnawaveConnectionError("Unexpected transport error") from e

        if response.is_success:
            return response

        try:
            error_data = response.json()
        except json.JSONDecodeError:
            error_data = response.text

        if response.status_code == 404:
            logger.info(
                "Remnawave API request | Status {} | URL: {} | Body: {}",
                response.status_code,
                response.url,
                error_data,
            )
            raise RemnawaveNotFoundError("Not Found")

        logger.error(
            "Remnawave API request failed | Status: {} | URL: {} | Body: {}",
            response.status_code,
            response.url,
            error_data,
        )

        if response.status_code == 400:
            raise RemnawaveValidationError("Invalid request data", payload=error_data)
        if response.status_code >= 500:
            raise RemnawaveServerError(
                f"Server error: {response.status_code}", payload=error_data
            )

        raise RemnawaveUnexpectedStatusError(
            f"Unexpected status: {response.status_code}", payload=error_data
        )

    async def create_user(
        self, payload: RemnawaveCreateUserRequest
    ) -> RemnawaveUserResponse:
        response = await self._send_request(
            method="POST",
            endpoint="/api/users",
            json_data=payload.model_dump(mode="json"),
        )
        data = response.json()
        return RemnawaveUserResponse.model_validate(data.get("response", data))

    async def delete_user(self, uuid: str) -> bool:
        try:
            await self._send_request(method="DELETE", endpoint=f"/api/users/{uuid}")
        except RemnawaveNotFoundError:
            return False
        return True

    async def get_user_by_uuid(self, uuid: str):
        response = await self._send_request(method="GET", endpoint=f"/api/users/{uuid}")
        data = response.json()
        return RemnawaveUserResponse.model_dump(data.get("response", data))
