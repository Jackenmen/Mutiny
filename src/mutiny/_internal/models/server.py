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

from typing import TYPE_CHECKING, Any, Optional, final

from .attachment import Attachment
from .bases import StatefulModel, StatefulResource
from .permissions import ChannelPermissions, ServerPermissions

if TYPE_CHECKING:
    from ..state import State

__all__ = ("Category", "SystemMessageChannels", "Role", "Member", "Server")


@final
class Category(StatefulResource):
    __slots__ = ("title", "channel_ids")

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.id: str = raw_data["id"]
        self.title: str = raw_data["title"]
        self.channel_ids: list[str] = raw_data["channels"]


@final
class SystemMessageChannels(StatefulModel):
    __slots__ = ("user_joined_id", "user_left_id", "user_kicked_id", "user_banned_id")

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.user_joined_id: Optional[str] = raw_data.get("user_joined")
        self.user_left_id: Optional[str] = raw_data.get("user_left")
        self.user_kicked_id: Optional[str] = raw_data.get("user_kicked")
        self.user_banned_id: Optional[str] = raw_data.get("user_banned")


@final
class Role(StatefulModel):
    __slots__ = (
        "name",
        "server_permissions",
        "channel_permissions",
        "colour",
        "hoist",
        "rank",
    )

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.name = raw_data["name"]
        self.server_permissions = ServerPermissions(raw_data["permissions"][0])
        self.channel_permissions = ChannelPermissions(raw_data["permissions"][1])
        self.hoist = raw_data.get("hoist", False)
        self.rank = raw_data["rank"]


@final
class Member(StatefulModel):
    __slots__ = ("server_id", "user_id", "nickname", "avatar", "role_ids")

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id: str = raw_data["_id"]["server"]
        self.user_id: str = raw_data["_id"]["user"]
        self.nickname: Optional[str] = raw_data.get("nickname")
        self.avatar = Attachment._from_raw_data(state, raw_data.get("avatar"))
        self.role_ids: list[str] = raw_data.get("roles", [])


@final
class Server(StatefulResource):
    __slots__ = (
        "nonce",
        "owner_id",
        "name",
        "description",
        "channel_ids",
        "categories",
        "system_message_channels",
        "roles",
        "default_server_permissions",
        "default_channel_permissions",
        "icon",
        "banner",
        "_members",
    )

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.id: str = raw_data["_id"]
        self.nonce: Optional[str] = raw_data.get("nonce")
        self.owner_id: str = raw_data["owner"]
        self.name: str = raw_data["name"]
        self.description: Optional[str] = raw_data.get("description")
        self.channel_ids: list[str] = raw_data["channels"]
        self.categories: dict[str, Category] = {
            category_data["id"]: Category(state, category_data)
            for category_data in raw_data.get("categories", [])
        }
        self.system_message_channels = SystemMessageChannels(
            state, raw_data.get("system_messages", {})
        )
        self.roles: dict[str, Role] = {
            role_id: Role(state, role_data)
            for role_id, role_data in raw_data.get("roles", {}).items()
        }
        self.default_server_permissions = ServerPermissions(
            raw_data["default_permissions"][0]
        )
        self.default_channel_permissions = ServerPermissions(
            raw_data["default_permissions"][1]
        )
        self.icon = Attachment._from_raw_data(state, raw_data.get("icon"))
        self.banner = Attachment._from_raw_data(state, raw_data.get("banner"))
        self._members: dict[str, Member] = {}
