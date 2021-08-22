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

from .gateway import GatewayClient
from .models.channel import Channel
from .models.server import Server
from .models.user import User
from .rest import RESTClient


class State:
    __slots__ = ("gateway", "rest", "channels", "servers", "users", "user")

    gateway: GatewayClient
    rest: RESTClient
    user: User

    def __init__(self) -> None:
        # caches
        self.channels: dict[str, Channel] = {}
        self.servers: dict[str, Server] = {}
        self.users: dict[str, User] = {}
