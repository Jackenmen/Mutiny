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

from typing import TYPE_CHECKING, Any, Optional, Union, final

from ... import events
from .attachment import Attachment
from .bases import ParserData, StatefulResource, UpdateFieldMissing, field
from .permissions import ChannelPermissions

if TYPE_CHECKING:
    from ..state import State

    _UpdateEvent = Union[
        events.ChannelUpdateEvent,
        events.ChannelGroupJoinEvent,
        events.ChannelGroupLeaveEvent,
        events.MessageEvent,
    ]

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
    id: str = field("_id")
    channel_type: str = field("channel_type")
    nonce: Optional[str] = field("nonce", default=None)

    @classmethod
    def _from_dict(cls, state: State, raw_data: dict[str, Any]) -> Channel:
        channel_type = raw_data["channel_type"]
        channel_cls = CHANNEL_TYPES.get(channel_type, UnknownChannel)
        return channel_cls(state, raw_data)

    def _update_from_event(self, event: _UpdateEvent) -> None:
        if type(event) is events.ChannelUpdateEvent:
            self._update_from_dict(event.data)


@final
class UnknownChannel(Channel):
    __slots__ = ()


@final
class SavedMessages(Channel):
    user_id: str = field("user")


@final
class DirectMessage(Channel):
    active: bool = field("active")
    recipient_ids: list[str] = field("recipients")
    last_message_id: Optional[str] = field("last_message", factory=True, default={})

    def _last_message_id_parser(self, parser_data: ParserData) -> Optional[str]:
        last_message_id = parser_data.get_field().get("_id")
        if not parser_data.init and last_message_id is None:
            raise UpdateFieldMissing(("last_message", "_id"))
        return last_message_id

    def _update_from_event(self, event: _UpdateEvent) -> None:
        if type(event) is events.MessageEvent:
            if event.message.content is not None:
                self.raw_data["last_message"] = {
                    "_id": event.message.id,
                    "author": event.message.author_id,
                    "short": event.message.content[:128],
                }
                self.last_message_id = event.message.id
        elif type(event) is events.ChannelGroupJoinEvent:
            # this list is the same object as raw_data["recipients"]
            self.recipient_ids.append(event.user_id)
        elif type(event) is events.ChannelGroupLeaveEvent:
            # this list is the same object as raw_data["recipients"]
            self.recipient_ids.remove(event.user_id)
        else:
            self._update_from_dict(event.data)


@final
class Group(Channel):
    recipient_ids: list[str] = field("recipients")
    name: str = field("name")
    owner_id: str = field("owner")
    description: Optional[str] = field("description", default=None)
    last_message_id: Optional[str] = field("last_message", factory=True, default={})
    icon: Optional[Attachment] = field("icon", factory=True, default=None)
    permissions: ChannelPermissions = field("permissions", factory=True, default=0)

    def _last_message_id_parser(self, parser_data: ParserData) -> Optional[str]:
        return parser_data.get_field().get("_id")

    def _icon_parser(self, parser_data: ParserData) -> Optional[Attachment]:
        return Attachment._from_raw_data(self._state, parser_data.get_field())

    def _permissions_parser(self, parser_data: ParserData) -> ChannelPermissions:
        return ChannelPermissions(parser_data.get_field())

    def _update_from_event(self, event: _UpdateEvent) -> None:
        if type(event) is events.MessageEvent:
            if event.message.content is not None:
                self.raw_data["last_message"] = {
                    "_id": event.message.id,
                    "author": event.message.author_id,
                    "short": event.message.content[:128],
                }
                self.last_message_id = event.message.id
        elif type(event) is events.ChannelGroupJoinEvent:
            # this list is the same object as raw_data["recipients"]
            self.recipient_ids.append(event.user_id)
        elif type(event) is events.ChannelGroupLeaveEvent:
            # this list is the same object as raw_data["recipients"]
            self.recipient_ids.remove(event.user_id)
        else:
            if event.clear == "Icon":
                self.raw_data.pop("icon", None)
                self.icon = None
            elif event.clear == "Description":
                self.raw_data.pop("description", None)
                self.description = None
            self._update_from_dict(event.data)


@final
class TextChannel(Channel):
    server_id: str = field("server")
    name: str = field("name")
    description: Optional[str] = field("description", default=None)
    icon: Optional[Attachment] = field("icon", factory=True, default=None)
    default_permissions: ChannelPermissions = field(
        "default_permissions", factory=True, default=0
    )
    role_permissions: dict[str, ChannelPermissions] = field(
        "role_permissions", factory=True, default={}
    )
    last_message_id: Optional[str] = field("last_message", default=None)

    def _icon_parser(self, parser_data: ParserData) -> Optional[Attachment]:
        return Attachment._from_raw_data(self._state, parser_data.get_field())

    def _default_permissions_parser(
        self, parser_data: ParserData
    ) -> ChannelPermissions:
        return ChannelPermissions(parser_data.get_field())

    def _role_permissions_parser(
        self, parser_data: ParserData
    ) -> dict[str, ChannelPermissions]:
        return {
            role_id: ChannelPermissions(perm_value)
            for role_id, perm_value in parser_data.get_field().items()
        }

    def _update_from_event(self, event: _UpdateEvent) -> None:
        if type(event) is events.MessageEvent:
            if event.message.content is not None:
                self.raw_data["last_message"] = self.last_message_id = event.message.id
        elif type(event) is events.ChannelUpdateEvent:
            if event.clear == "Icon":
                self.raw_data.pop("icon", None)
                self.icon = None
            elif event.clear == "Description":
                self.raw_data.pop("description", None)
                self.description = None
            self._update_from_dict(event.data)


@final
class VoiceChannel(Channel):
    server_id: str = field("server")
    name: str = field("name")
    description: Optional[str] = field("description", default=None)
    icon: Optional[Attachment] = field("icon", factory=True, default=None)
    default_permissions: ChannelPermissions = field(
        "default_permissions", factory=True, default=0
    )
    role_permissions: dict[str, ChannelPermissions] = field(
        "role_permissions", factory=True, default={}
    )

    def _icon_parser(self, parser_data: ParserData) -> Optional[Attachment]:
        return Attachment._from_raw_data(self._state, parser_data.get_field())

    def _default_permissions_parser(
        self, parser_data: ParserData
    ) -> ChannelPermissions:
        return ChannelPermissions(parser_data.get_field())

    def _role_permissions_parser(
        self, parser_data: ParserData
    ) -> dict[str, ChannelPermissions]:
        return {
            role_id: ChannelPermissions(perm_value)
            for role_id, perm_value in parser_data.get_field().items()
        }

    def _update_from_event(self, event: _UpdateEvent) -> None:
        if type(event) is events.ChannelUpdateEvent:
            if event.clear == "Icon":
                self.raw_data.pop("icon", None)
                self.icon = None
            elif event.clear == "Description":
                self.raw_data.pop("description", None)
                self.description = None
            self._update_from_dict(event.data)


CHANNEL_TYPES = {
    "SavedMessages": SavedMessages,
    "DirectMessage": DirectMessage,
    "Group": Group,
    "TextChannel": TextChannel,
    "VoiceChannel": VoiceChannel,
}
