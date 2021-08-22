# Copyright 2021 Jakub Kuczys (https://github.com/jack1142)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import json as json_
from typing import TYPE_CHECKING, Any

import aiohttp
from aiohttp import hdrs

from .authentication_data import AuthenticationData

if TYPE_CHECKING:
    from .client import Client
    from .state import State

__all__ = ("RESTClient",)


class RESTClient:
    def __init__(
        self,
        *,
        session: aiohttp.ClientSession,
        authentication_data: AuthenticationData,
        api_url: str,
        state: State,
    ) -> None:
        self.session = session
        self.authentication_data = authentication_data
        self.api_url = api_url
        self.configuration: dict[str, Any] = {}
        self.headers = self.authentication_data.to_headers()
        self.state = state
        state.rest = self

    @classmethod
    async def from_client(cls, client: Client) -> RESTClient:
        rest = RESTClient(
            session=client._session,
            authentication_data=client._authentication_data,
            api_url=client.api_url,
            state=client._state,
        )
        await rest.fetch_configuration()
        return rest

    @property
    def cdn_url(self) -> str:
        return self.configuration["features"]["autumn"]["url"]

    @property
    def gateway_url(self) -> str:
        return self.configuration["ws"]

    async def request(
        self, method: str, url: str, *, headers: dict[str, Any] = {}, json: Any = None
    ) -> Any:
        async with self.session.request(
            method, url, headers=headers, json=json
        ) as resp:
            text = await resp.text()
            data: Any = ...
            if resp.headers.get(hdrs.CONTENT_TYPE, "") == "application/json":
                data = json_.loads(text)
            if resp.status in (200, 204):
                return data
            else:
                ...

    async def fetch_configuration(self) -> dict[str, Any]:
        self.configuration = await self.request(hdrs.METH_GET, self.api_url)
        return self.configuration
