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
from .bases import ParserData, StatefulModel, StatefulResource, field
from .permissions import ChannelPermissions, ServerPermissions

if TYPE_CHECKING:
    from ...events import (
        ServerMemberUpdateEvent,
        ServerRoleUpdateEvent,
        ServerUpdateEvent,
    )

__all__ = ("Category", "SystemMessageChannels", "Role", "Member", "Server")


@final
class Category(StatefulResource):
    id: str = field("id")
    title: str = field("title")
    channel_ids: list[str] = field("channels")


@final
class SystemMessageChannels(StatefulModel):
    user_joined_id: Optional[str] = field("user_joined", default=None)
    user_left_id: Optional[str] = field("user_left", default=None)
    user_kicked_id: Optional[str] = field("user_kicked", default=None)
    user_banned_id: Optional[str] = field("user_banned", default=None)


@final
class Role(StatefulModel):
    name: str = field("name")
    server_permissions: ServerPermissions = field(keys=("permissions", 0), factory=True)
    channel_permissions: ChannelPermissions = field(
        keys=("permissions", 1), factory=True
    )
    colour: Optional[str] = field("colour", default=None)
    hoist: bool = field("hoist", default=False)
    rank: int = field("rank")

    def _server_permissions_parser(self, parser_data: ParserData) -> ServerPermissions:
        return ServerPermissions(parser_data.get_field())

    def _channel_permissions_parser(
        self, parser_data: ParserData
    ) -> ChannelPermissions:
        return ChannelPermissions(parser_data.get_field())

    def _update_from_event(self, event: ServerRoleUpdateEvent) -> None:
        if event.clear == "Colour":
            self.colour = None
        self._update_from_dict(event.data)


@final
class Member(StatefulModel):
    server_id: str = field(keys=("_id", "server"))
    user_id: str = field(keys=("_id", "user"))
    nickname: Optional[str] = field("nickname", default=None)
    avatar: Optional[Attachment] = field("avatar", factory=True, default=None)
    role_ids: list[str] = field("roles", default_factory=list)

    def _avatar_parser(self, parser_data: ParserData) -> Optional[Attachment]:
        return Attachment._from_raw_data(self._state, parser_data.get_field())

    def _update_from_event(self, event: ServerMemberUpdateEvent) -> None:
        if event.clear == "Nickname":
            self.nickname = None
        elif event.clear == "Avatar":
            self.avatar = None
        self._update_from_dict(event.data)


@final
class Server(StatefulResource):
    id: str = field("_id")
    nonce: Optional[str] = field("nonce", default=None)
    owner_id: str = field("owner")
    name: str = field("name")
    description: Optional[str] = field("description", default=None)
    channel_ids: list[str] = field("channels")
    categories: dict[str, Any] = field("categories", factory=True, default=[])
    system_message_channels: SystemMessageChannels = field(
        "system_messages", factory=True, default_factory=dict
    )
    roles: dict[str, Any] = field("roles", factory=True, default={})
    default_server_permissions: ServerPermissions = field(
        keys=("default_permissions", 0), factory=True
    )
    default_channel_permissions: ChannelPermissions = field(
        keys=("default_permissions", 1), factory=True
    )
    icon: Optional[Attachment] = field("icon", factory=True, default=None)
    banner: Optional[Attachment] = field("banner", factory=True, default=None)
    # small abuse that allows me to not define __init__ or parser
    _members: dict[str, Member] = field("some placeholder", default_factory=dict)

    def _categories_parser(self, parser_data: ParserData) -> dict[str, Any]:
        return {
            category_data["id"]: Category(self._state, category_data)
            for category_data in parser_data.get_field()
        }

    def _system_message_channels_parser(
        self, parser_data: ParserData
    ) -> SystemMessageChannels:
        return SystemMessageChannels(self._state, parser_data.get_field())

    def _roles_parser(self, parser_data: ParserData) -> dict[str, Any]:
        return {
            role_id: Role(self._state, role_data)
            for role_id, role_data in parser_data.get_field().items()
        }

    def _default_server_permissions_parser(
        self, parser_data: ParserData
    ) -> ServerPermissions:
        return ServerPermissions(parser_data.get_field())

    def _default_channel_permissions_parser(
        self, parser_data: ParserData
    ) -> ChannelPermissions:
        return ChannelPermissions(parser_data.get_field())

    def _icon_parser(self, parser_data: ParserData) -> Optional[Attachment]:
        return Attachment._from_raw_data(self._state, parser_data.get_field())

    def _banner_parser(self, parser_data: ParserData) -> Optional[Attachment]:
        return Attachment._from_raw_data(self._state, parser_data.get_field())

    def _update_from_event(self, event: ServerUpdateEvent) -> None:
        if event.clear == "Icon":
            self.raw_data.pop("icon", None)
            self.icon = None
        elif event.clear == "Banner":
            self.raw_data.pop("banner", None)
            self.banner = None
        elif event.clear == "Description":
            self.raw_data.pop("description", None)
            self.description = None
        self._update_from_dict(event.data)
