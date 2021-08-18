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

import asyncio
import json
from typing import TYPE_CHECKING, Any, Optional

import aiohttp

from ..events import Event
from .authentication_data import AuthenticationData
from .event_handler import EventHandler

if TYPE_CHECKING:
    from .client import Client

__all__ = ("GatewayClient",)


class GatewayClient:
    ws: aiohttp.ClientWebSocketResponse

    def __init__(
        self,
        *,
        session: aiohttp.ClientSession,
        url: str,
        authentication_data: AuthenticationData,
        event_handler: EventHandler,
    ) -> None:
        self.session = session
        self.url = url
        self.authentication_data = authentication_data
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.event_handler = event_handler

    @classmethod
    def from_client(cls, client: Client) -> GatewayClient:
        gateway = GatewayClient(
            session=client._session,
            url=client._rest.gateway_url,
            authentication_data=client._authentication_data,
            event_handler=client._event_handler,
        )
        return gateway

    async def close(self) -> None:
        if not self.ws.closed:
            await self.ws.close()
        self.stop_heartbeat()

    async def connect(self) -> None:
        self.ws = await self.session.ws_connect(self.url, timeout=30.0, max_msg_size=0)
        await self.authenticate()
        self.start_heartbeat()

        await self.poll_loop()

    async def poll_loop(self) -> None:
        async for msg in self.ws:
            if msg.type is aiohttp.WSMsgType.ERROR:
                raise msg.data
            if msg.type is not aiohttp.WSMsgType.TEXT:
                raise RuntimeError(f"got {msg}, but can't handle its type")

            event = Event.from_dict(json.loads(msg.data))
            self.event_handler.dispatch(event)

    async def authenticate(self) -> None:
        payload = {
            "type": "Authenticate",
            **self.authentication_data.to_dict(),
        }
        await self.send_json(payload)

    async def begin_typing(self, channel_id: str) -> None:
        payload = {
            "type": "BeginTyping",
            "channel": channel_id,
        }
        await self.send_json(payload)

    async def end_typing(self, channel_id: str) -> None:
        payload = {
            "type": "EndTyping",
            "channel": channel_id,
        }
        await self.send_json(payload)

    async def ping(self, time: int = 0) -> None:
        payload: dict[str, Any] = {"type": "Ping"}
        if time:
            payload["time"] = time
        await self.send_json(payload)

    def start_heartbeat(self) -> None:
        self.stop_heartbeat()
        self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())

    def stop_heartbeat(self) -> None:
        if self.heartbeat_task is not None:
            self.heartbeat_task.cancel()
            self.heartbeat_task = None

    async def heartbeat_loop(self) -> None:
        while not self.ws.closed:
            await self.ping()
            await asyncio.sleep(10)

    async def send_json(self, payload: Any) -> None:
        await self.ws.send_json(payload)
