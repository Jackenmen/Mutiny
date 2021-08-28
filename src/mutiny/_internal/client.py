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

import asyncio
from typing import Callable, Optional, TypeVar, overload

import aiohttp

from ..events import Event
from .authentication_data import AuthenticationData
from .event_handler import EventHandler, EventListener, EventT, EventT_contra
from .gateway import HAS_MSGPACK, GatewayClient, GatewayMessageFormat
from .rest import RESTClient
from .state import State

T = TypeVar("T")

__all__ = ("Client",)


class Client:
    """
    Client that connects to the Revolt's APIs. This class is used to interact with
    all of the Revolt's services.

    Examples:
        Creating a client for a bot account:

        .. code-block:: python

            import os
            import mutiny

            client = mutiny.Client(token=os.environ["BOT_TOKEN"])

        Creating a client for a user account:

        .. code-block:: python

            import os
            import mutiny

            client = mutiny.Client(
                user_id=os.environ["BOT_USER_ID"],
                session_token=os.environ["BOT_SESSION_TOKEN"],
            )

    Parameters:
        token:
            The bot's token. This should be passed for bot accounts.
        user_id:
            The user ID. This should be passed for user accounts.
        session_token:
            User's session token. This should be passed for user accounts.
        api_url:
            The API URL. Used for self-hosted Revolt servers.
        gateway_format:
            Format to be used by the gateway. When not passed, the format will be chosen
            based on the installed dependencies. ``msgpack`` is preferred over ``json``.

            .. tip::

                To use msgpack, you need to install Mutiny with the ``msgpack`` extra,
                e.g.::

                    pip install -U mutiny[msgpack]
    """

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

    async def wait_for(
        self,
        event_cls: type[EventT],
        /,
        *,
        check: Optional[Callable[[EventT], bool]] = None,
        timeout: Optional[int] = None,
    ) -> EventT:
        future = self._event_handler.add_waiter(event_cls, check=check)
        # wait_for() automatically cancels the future on timeout so
        # we don't need any additional handling here
        return await asyncio.wait_for(future, timeout=timeout)

    async def start(self) -> None:
        """A shorthand function for `login()` + `connect()`."""
        await self.login()
        await self.connect()

    async def login(self) -> None:
        """Logs in the client. Necessary to make the REST API requests."""
        self._session = aiohttp.ClientSession()
        self._rest = await RESTClient.from_client(self)

    async def connect(self) -> None:
        """
        Creates a websocket connection and lets the websocket listen to messages
        from the Revolt's gateway.

        This is a loop that runs the entire event systems. Control is not resumed until
        the WebSocket connection is terminated.

        .. note::

            This requires `login()` to be called before it can be used.
        """
        self._gateway = GatewayClient.from_client(self)
        await self._gateway.connect()

    async def close(self) -> None:
        """
        Closes the client and its connections.

        This should be called before closing the application.
        """
        if self._closed:
            return
        await self._gateway.close()
        await self._session.close()

    def add_listener(
        self, listener: EventListener, *, event_cls: Optional[type[Event]] = None
    ) -> None:
        """
        Register a function to listen to an event.

        Examples:
            Registering a bound method of a class as an event listener:

            .. code-block:: python

                class CoolClass:
                    def __init__(self, client):
                        self.client = client

                    async def message_listener(self, event: mutiny.events.MessageEvent):
                        print(f"Received a message: {event.message!r}")

                    def register_listeners(self):
                        self.client.add_listener(self.message_listener)

                cool_class = CoolClass(client)
                cool_class.register_listeners()

        Parameters:
            listener(event listener): A function to register as an event listener.
            event_cls:
                Event to listen to. If omitted, the type annotation of
                the first argument of the passed function will be used.

        """
        self._event_handler.add_listener(listener, event_cls=event_cls)

    @overload
    def listen(
        self, event_cls: type[EventT_contra]
    ) -> Callable[[EventListener[EventT_contra, T]], EventListener[EventT_contra, T]]:
        ...

    @overload
    def listen(
        self, event_cls: None = ...
    ) -> Callable[[EventListener[EventT_contra, T]], EventListener[EventT_contra, T]]:
        ...

    def listen(
        self, event_cls: Optional[type[Event]] = None
    ) -> Callable[[EventListener[EventT_contra, T]], EventListener[EventT_contra, T]]:
        """
        Register a function to listen to an event.

        Examples:
            Event listener can be added by defining a single argument function
            decorated with ``@client.listen()`` and with its argument annotated
            with an appropriate event type:

            .. code-block:: python

                @client.listen()
                async def function(event: mutiny.events.MessageEvent):
                    print(f"Received a message: {event.message!r}")

            Alternatively, you can omit the type annotation or use an incompatible one
            if you pass the event class as an argument to the decorator:

            .. code-block:: python

                @client.listen(mutiny.events.MessageEvent)
                async def function(event):
                    print(f"Received a message: {event.message!r}")

        Parameters:
            event_cls:
                Event to listen to. If omitted, the type annotation of
                the first argument of the passed function will be used.

        Returns:
            The passed function, unchanged.
        """

        def deco(
            func: EventListener[EventT_contra, T]
        ) -> EventListener[EventT_contra, T]:
            self.add_listener(func, event_cls=event_cls)
            return func

        return deco
