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
from .bases import StatefulResource
from .permissions import ChannelPermissions

if TYPE_CHECKING:
    from ..state import State

__all__ = (
    "Channel",
    "UnknownChannel",
    "SavedMessages",
    "DirectMessage",
    "Group",
    "TextChannel",
    "VoiceChannel",
)


class Channel(StatefulResource):
    __slots__ = ("channel_type", "nonce")

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.id: str = raw_data["_id"]
        self.channel_type: str = raw_data["channel_type"]
        self.nonce: Optional[str] = raw_data.get("nonce")

    @classmethod
    def _from_dict(cls, state: State, raw_data: dict[str, Any]) -> Channel:
        channel_type = raw_data["channel_type"]
        channel_cls = CHANNEL_TYPES.get(channel_type, UnknownChannel)
        return channel_cls(state, raw_data)


@final
class UnknownChannel(Channel):
    __slots__ = ()


@final
class SavedMessages(Channel):
    __slots__ = ("user_id",)

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.user_id: str = raw_data["user"]


@final
class DirectMessage(Channel):
    __slots__ = ("active", "recipient_ids", "last_message_id")
    active: bool
    recipient_ids: list[str]
    last_message_id: Optional[str]

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.active: bool = raw_data["active"]
        self.recipient_ids: list[str] = raw_data["recipients"]
        self.last_message_id: Optional[str] = raw_data.get("last_message", {}).get(
            "_id"
        )


@final
class Group(Channel):
    __slots__ = (
        "recipient_ids",
        "name",
        "owner_id",
        "description",
        "last_message_id",
        "icon",
        "permissions",
    )

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.recipient_ids: list[str] = raw_data["recipients"]
        self.name: str = raw_data["name"]
        self.owner_id: str = raw_data["owner"]
        self.description: Optional[str] = raw_data.get("description")
        self.last_message_id: Optional[str] = raw_data.get("last_message", {}).get(
            "_id"
        )
        self.icon = Attachment._from_raw_data(state, raw_data.get("icon"))
        self.permissions = ChannelPermissions(raw_data.get("permissions", 0))


@final
class TextChannel(Channel):
    __slots__ = (
        "server_id",
        "name",
        "description",
        "icon",
        "default_permissions",
        "role_permissions",
        "last_message_id",
    )

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id: str = raw_data["server"]
        self.name: str = raw_data["name"]
        self.description: Optional[str] = raw_data.get("description")
        self.icon = Attachment._from_raw_data(state, raw_data.get("icon"))
        self.default_permissions = ChannelPermissions(
            raw_data.get("default_permissions", 0)
        )
        self.role_permissions: dict[str, ChannelPermissions] = {
            role_id: ChannelPermissions(perm_value)
            for role_id, perm_value in raw_data.get("role_permissions", {}).items()
        }
        self.last_message_id: Optional[str] = raw_data.get("last_message")


@final
class VoiceChannel(Channel):
    __slots__ = (
        "server_id",
        "name",
        "description",
        "icon",
        "default_permissions",
        "role_permissions",
    )

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id: str = raw_data["server"]
        self.name: str = raw_data["name"]
        self.description: Optional[str] = raw_data.get("description")
        self.icon = Attachment._from_raw_data(state, raw_data.get("icon"))
        self.default_permissions = ChannelPermissions(
            raw_data.get("default_permissions", 0)
        )
        self.role_permissions: dict[str, ChannelPermissions] = {
            role_id: ChannelPermissions(perm_value)
            for role_id, perm_value in raw_data.get("role_permissions", {}).items()
        }


CHANNEL_TYPES = {
    "SavedMessages": SavedMessages,
    "DirectMessage": DirectMessage,
    "Group": Group,
    "TextChannel": TextChannel,
    "VoiceChannel": VoiceChannel,
}
