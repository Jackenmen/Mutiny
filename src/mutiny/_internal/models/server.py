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

"""Server models"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, final

from ..bit_fields import ChannelPermissions, ServerFlags, ServerPermissions
from .attachment import Attachment
from .bases import ParserData, StatefulModel, StatefulResource, field

if TYPE_CHECKING:
    from ...events import (
        ServerMemberUpdateEvent,
        ServerRoleUpdateEvent,
        ServerUpdateEvent,
    )

__all__ = (
    "Server",
    "Category",
    "Member",
    "Role",
    "SystemMessageChannels",
)


@final
class Category(StatefulResource):
    """
    Category()

    Represents a server channel category.

    Attributes:
        id: The category ID.
        title: The category title.
        channel_ids: List of the channel IDs belonging to this category.
    """

    id: str = field("id")
    title: str = field("title")
    channel_ids: list[str] = field("channels")


@final
class SystemMessageChannels(StatefulModel):
    """
    SystemMessageChannels()

    Represents a server's system message channels configuration.

    Attributes:
        user_joined_id: The ID of the channel used for "user joined" messages, if any.
        user_left_id: The ID of the channel used for "user left" messages, if any.
        user_kicked_id: The ID of the channel used for "user kicked" messages, if any.
        user_banned_id: The ID of the channel used for "user banned" messages, if any.
    """

    user_joined_id: Optional[str] = field("user_joined", default=None)
    user_left_id: Optional[str] = field("user_left", default=None)
    user_kicked_id: Optional[str] = field("user_kicked", default=None)
    user_banned_id: Optional[str] = field("user_banned", default=None)


@final
class Role(StatefulResource):
    """
    Role()

    Represents a role in a server.

    Attributes:
        id: The ID of the role.
        name: The name of the role.
        server_permissions: The role's server permissions.
        channel_permissions: The role's channel permissions.
        colour: The role's colour.
        hoist: Indicates if the role will be displayed separately on the members list.
        rank:
            The role's ranking. A role with a smaller number will have permissions over
            the roles with larger numbers.
    """

    id: str = field("id")
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
class Member(StatefulResource):
    """
    Member()

    Represents a member in a server.

    Attributes:
        id: The member ID (equivalent to user ID).
        server_id: The ID of the member's server.
        nickname: The member's server nickname.
        avatar: The member's server avatar.
        role_ids: List of the role IDs the member has.
    """

    id: str = field(keys=("_id", "user"))
    server_id: str = field(keys=("_id", "server"))
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
    """
    Server()

    Represents a server.

    Attributes:
        id: The server ID.
        nonce: Nonce value, used to prevent double requests to create objects.
        owner_id: The user ID of the server's owner.
        name: The name of the server.
        description: The description of the server if provided.
        channel_ids: List of the channel IDs in the server.
        categories: Mapping of the category ID to category in the server.
        system_message_channels: The server's system message channels configuration.
        roles: Mapping of the role ID to role in the server.
        default_server_permissions: The default server permissions.
        default_channel_permissions: The default channel permissions in the server.
        icon: The server's icon if provided.
        banner: The server's banner if provided.
    """

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
    nsfw: bool = field("nsfw", default=False)
    flags: ServerFlags = field("flags", factory=True, default=0)
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
        roles = {}
        for role_id, role_data in parser_data.get_field().items():
            role_data["id"] = role_id
            roles[role_id] = Role(self._state, role_data)
        return roles

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

    def _flags_parser(self, parser_data: ParserData) -> ServerFlags:
        return ServerFlags(parser_data.get_field())

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
