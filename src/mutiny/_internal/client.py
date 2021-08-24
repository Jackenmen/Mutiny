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

from typing import Callable, Optional, TypeVar, overload

import aiohttp

from ..events import Event
from .authentication_data import AuthenticationData
from .event_handler import EventHandler, EventListener, EventT_contra
from .gateway import HAS_MSGPACK, GatewayClient, GatewayMessageFormat
from .rest import RESTClient
from .state import State

T = TypeVar("T")

__all__ = ("Client",)


class Client:
    _session: aiohttp.ClientSession
    _gateway: GatewayClient
    _rest: RESTClient

    @overload
    def __init__(
        self,
        *,
        token: str,
        user_id: None = ...,
        session_token: None = ...,
        api_url: str = ...,
        gateway_format: Optional[GatewayMessageFormat] = ...,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        token: None = ...,
        user_id: str,
        session_token: str,
        api_url: str = ...,
        gateway_format: Optional[GatewayMessageFormat] = ...,
    ) -> None:
        ...

    def __init__(
        self,
        *,
        token: Optional[str] = None,
        user_id: Optional[str] = None,
        session_token: Optional[str] = None,
        api_url: str = "https://api.revolt.chat",
        gateway_format: Optional[GatewayMessageFormat] = None,
    ) -> None:
        self._authentication_data = AuthenticationData(
            token=token, user_id=user_id, session_token=session_token
        )
        self._event_handler = EventHandler()
        self.api_url = api_url
        if gateway_format == "msgpack" and not HAS_MSGPACK:
            raise RuntimeError(
                "'msgpack' format requires you to install Mutiny with `msgpack` extra."
            )
        if gateway_format is None:
            gateway_format = "msgpack" if HAS_MSGPACK else "json"
        self._gateway_format: GatewayMessageFormat = gateway_format
        self._state = State()
        self._closed = False

    def __repr__(self) -> str:
        return f"<mutiny.{self.__class__.__name__} object at {hex(id(self))}>"

    async def start(self) -> None:
        await self.login()
        await self.connect()

    async def login(self) -> None:
        self._session = aiohttp.ClientSession()
        self._rest = await RESTClient.from_client(self)

    async def connect(self) -> None:
        self._gateway = GatewayClient.from_client(self)
        await self._gateway.connect()

    async def close(self) -> None:
        if self._closed:
            return
        await self._gateway.close()
        await self._session.close()

    def add_listener(
        self, listener: EventListener, *, event_cls: Optional[type[Event]] = None
    ) -> None:
        self._event_handler.add_listener(listener, event_cls=event_cls)

    def listen(
        self, event_cls: Optional[type[Event]] = None
    ) -> Callable[[EventListener[EventT_contra, T]], EventListener[EventT_contra, T]]:
        def deco(
            func: EventListener[EventT_contra, T]
        ) -> EventListener[EventT_contra, T]:
            self.add_listener(func, event_cls=event_cls)
            return func

        return deco
