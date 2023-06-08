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

"""Channels"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union, final

from ... import events
from ..bit_fields import Permissions
from .attachment import Attachment
from .bases import ParserData, StatefulResource, field
from .permission_override import PermissionOverride

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
    "SavedMessagesChannel",
    "DMChannel",
    "GroupChannel",
    "TextChannel",
    "VoiceChannel",
)


class Channel(StatefulResource):
    """
    Channel()

    Base class for all channel classes.

    Attributes:
        id: The channel ID.
        type:
            The channel's type.

            .. note::

                Checking using ``type()`` or :func:`isinstance()` should be
                preferred over using this attribute.
    """

    id: str = field("_id")
    channel_type: str = field("channel_type")

    @classmethod
    def _from_dict(cls, state: State, raw_data: dict[str, Any]) -> Channel:
        channel_type = raw_data["channel_type"]
        channel_cls = CHANNEL_TYPES.get(channel_type, _UnknownChannel)
        return channel_cls(state, raw_data)

    def _update_from_event(self, event: _UpdateEvent) -> None:
        if type(event) is events.ChannelUpdateEvent:
            self._update_from_dict(event.data)


@final
class _UnknownChannel(Channel):
    __slots__ = ()


@final
class SavedMessagesChannel(Channel):
    """
    SavedMessagesChannel()

    Represent the 'Saved Notes' channel of a user.

    Attributes:
        user_id: The ID of a user who created and owns the channel.
    """

    user_id: str = field("user")


@final
class DMChannel(Channel):
    """
    DMChannel()

    Represents a direct message (DM) channel.

    Attributes:
        active: Indicates whether this DM is active.
        recipient_ids: List of user IDs who are participating in this DM.
        last_message_id:
            ID of the last message sent in this channel if any.

            .. note::

                This only includes non-system messages.
    """

    active: bool = field("active")
    recipient_ids: list[str] = field("recipients")
    last_message_id: Optional[str] = field("last_message_id", default=None)

    def _update_from_event(self, event: _UpdateEvent) -> None:
        if type(event) is events.MessageEvent:
            if event.message.content is not None:
                self.raw_data["last_message_id"] = event.message.id
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
class GroupChannel(Channel):
    """
    GroupChannel()

    Represents a group channel.

    Attributes:
        recipient_ids: List of user IDs who are participating in this channel.
        name: The channel's name.
        owner_id: The user ID of the owner of this channel.
        description: The channel's description if provided.
        last_message_id:
            ID of the last message sent in this channel if any.

            .. note::

                This only includes non-system messages.
        icon: The channel's icon if provided.
        permissions: The permissions in this channel.
    """

    recipient_ids: list[str] = field("recipients")
    name: str = field("name")
    owner_id: str = field("owner")
    description: Optional[str] = field("description", default=None)
    last_message_id: Optional[str] = field("last_message_id", default=None)
    icon: Optional[Attachment] = field("icon", factory=True, default=None)
    permissions: Permissions = field("permissions", factory=True, default=0)
    nsfw: bool = field("nsfw", default=False)

    def _icon_parser(self, parser_data: ParserData) -> Optional[Attachment]:
        return Attachment._from_raw_data(self._state, parser_data.get_field())

    def _permissions_parser(self, parser_data: ParserData) -> Permissions:
        return Permissions(parser_data.get_field())

    def _update_from_event(self, event: _UpdateEvent) -> None:
        if type(event) is events.MessageEvent:
            if event.message.content is not None:
                self.raw_data["last_message_id"] = event.message.id
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
    """
    TextChannel()

    Represents a server text channel.

    Attributes:
        server_id: The ID of the server the channel belongs to.
        name: The channel's name.
        description: The channel's description if provided.
        icon: The channel's icon if provided.
        default_permission_override: The default permission override in this channel.
        permission_overrides:
            The mapping of role ID to its permission override in this channel.
        last_message_id:
            ID of the last message sent in this channel if any.

            .. note::

                This only includes non-system messages.
        nsfw: Indicates whether this channel is Not Safe For Work (NSFW).
        archived: Indicates whether this channel is archived.
    """

    server_id: str = field("server")
    name: str = field("name")
    description: Optional[str] = field("description", default=None)
    icon: Optional[Attachment] = field("icon", factory=True, default=None)
    default_permission_override: PermissionOverride = field(
        "default_permissions", factory=True, default={"a": 0, "d": 0}
    )
    permission_overrides: dict[str, PermissionOverride] = field(
        "role_permissions", factory=True, default={}
    )
    last_message_id: Optional[str] = field("last_message_id", default=None)
    nsfw: bool = field("nsfw", default=False)
    archived: bool = field("archived", default=False)

    def _icon_parser(self, parser_data: ParserData) -> Optional[Attachment]:
        return Attachment._from_raw_data(self._state, parser_data.get_field())

    def _default_permission_override_parser(
        self, parser_data: ParserData
    ) -> PermissionOverride:
        return PermissionOverride(parser_data.get_field())

    def _permission_overrides_parser(
        self, parser_data: ParserData
    ) -> dict[str, PermissionOverride]:
        return {
            role_id: PermissionOverride(override_data)
            for role_id, override_data in parser_data.get_field().items()
        }

    def _update_from_event(self, event: _UpdateEvent) -> None:
        if type(event) is events.MessageEvent:
            if event.message.content is not None:
                self.raw_data["last_message_id"] = event.message.id
                self.last_message_id = event.message.id
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
    """
    VoiceChannel()

    Represents a server voice channel.

    Attributes:
        server_id: The ID of the server the channel belongs to.
        name: The channel's name.
        description: The channel's description if provided.
        icon: The channel's icon if provided.
        default_permission_override: The default permission override in this channel.
        permission_overrides:
            The mapping of role ID to its permission override in this channel.
    """

    server_id: str = field("server")
    name: str = field("name")
    description: Optional[str] = field("description", default=None)
    icon: Optional[Attachment] = field("icon", factory=True, default=None)
    default_permission_override: PermissionOverride = field(
        "default_permissions", factory=True, default={"a": 0, "d": 0}
    )
    permission_overrides: dict[str, PermissionOverride] = field(
        "role_permissions", factory=True, default={}
    )
    nsfw: bool = field("nsfw", default=False)

    def _icon_parser(self, parser_data: ParserData) -> Optional[Attachment]:
        return Attachment._from_raw_data(self._state, parser_data.get_field())

    def _default_permission_override_parser(
        self, parser_data: ParserData
    ) -> PermissionOverride:
        return PermissionOverride(parser_data.get_field())

    def _permission_overrides_parser(
        self, parser_data: ParserData
    ) -> dict[str, PermissionOverride]:
        return {
            role_id: PermissionOverride(override_data)
            for role_id, override_data in parser_data.get_field().items()
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
    "SavedMessages": SavedMessagesChannel,
    "DirectMessage": DMChannel,
    "Group": GroupChannel,
    "TextChannel": TextChannel,
    "VoiceChannel": VoiceChannel,
}
