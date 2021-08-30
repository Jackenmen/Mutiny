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
from typing import TYPE_CHECKING

from .gateway import GatewayClient
from .models.channel import Channel
from .models.server import Server
from .models.user import User
from .rest import RESTClient

if TYPE_CHECKING:
    from .client import Client


class State:
    user: User
    rest: RESTClient
    gateway: GatewayClient
    channels: dict[str, Channel]
    servers: dict[str, Server]
    users: dict[str, User]

    def __init__(self, client: Client) -> None:
        self.client = client
        self.ready = asyncio.Event()
        self.clear()

    def clear(self) -> None:
        try:
            del self.user
        except AttributeError:
            pass

        self.rest = RESTClient.from_state(self)
        self.gateway = GatewayClient.from_state(self)
        # caches
        self.channels: dict[str, Channel] = {}
        self.servers: dict[str, Server] = {}
        self.users: dict[str, User] = {}
        # ready event
        self.ready.clear()
