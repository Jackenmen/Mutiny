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

"""Messages"""

from __future__ import annotations

import datetime
from typing import Any, Optional, final

from ..utils import parse_datetime
from .attachment import Attachment
from .bases import Model, ParserData, StatefulResource, field
from .embed import Embed

__all__ = (
    "Message",
    "SystemMessage",
    "TextSystemMessage",
    "UserAddedSystemMessage",
    "UserRemovedSystemMessage",
    "UserJoinedSystemMessage",
    "UserLeftSystemMessage",
    "UserKickedSystemMessage",
    "UserBannedSystemMessage",
    "ChannelRenamedSystemMessage",
    "ChannelDescriptionChangedSystemMessage",
    "ChannelIconChangedSystemMessage",
)


class SystemMessage(Model):
    """
    SystemMessage()

    Base class for all system message classes.

    Attributes:
        type:
            The type of the system message.

            .. note::

                Checking using ``type()`` or :func:`isinstance()` should be
                preferred over using this attribute.
    """

    type: str = field("type")

    @classmethod
    def _from_dict(cls, raw_data: dict[str, Any]) -> SystemMessage:
        system_message_type = raw_data["type"]
        system_message_cls = SYSTEM_MESSAGE_TYPES.get(
            system_message_type, _UnknownSystemMessage
        )
        return system_message_cls(raw_data)


@final
class _UnknownSystemMessage(SystemMessage):
    __slots__ = ()


@final
class TextSystemMessage(SystemMessage):
    """
    TextSystemMessage()

    Represents a text system message.

    Attributes:
        content:
            The contents of the message.
    """

    content: str = field("content")


@final
class UserAddedSystemMessage(SystemMessage):
    """
    UserAddedSystemMessage()

    Represents a "user added" system message in group channels.

    Attributes:
        target_id:
            The ID of the user added to the channel.
        actor_id:
            The ID of the user who added the user to the channel.
    """

    target_id: int = field("id")
    actor_id: int = field("by")


@final
class UserRemovedSystemMessage(SystemMessage):
    """
    UserRemovedSystemMessage()

    Represents a "user removed" system message in group channels.

    Attributes:
        target_id:
            The ID of the user removed from the channel.
        actor_id:
            The ID of the user who removed the user from the channel.
    """

    target_id: int = field("id")
    actor_id: int = field("by")


@final
class UserJoinedSystemMessage(SystemMessage):
    """
    UserJoinedSystemMessage()

    Represents a "user joined" system message in server text channels.

    Attributes:
        user_id:
            The ID of the user who joined the server.
    """

    user_id: str = field("id")


@final
class UserLeftSystemMessage(SystemMessage):
    """
    UserLeftSystemMessage()

    Represents a "user left" system message in server text channels.

    Attributes:
        user_id:
            The ID of the user who left the server.
    """

    user_id: str = field("id")


@final
class UserKickedSystemMessage(SystemMessage):
    """
    UserKickedSystemMessage()

    Represents a "user kicked" system message in server text channels.

    Attributes:
        target_id:
            The ID of the user kicked from the server.
    """

    target_id: str = field("id")


@final
class UserBannedSystemMessage(SystemMessage):
    """
    UserBannedSystemMessage()

    Represents a "user banned" system message in server text channels.

    Attributes:
        target_id:
            The ID of the user banned from the server.
    """

    target_id: str = field("id")


@final
class ChannelRenamedSystemMessage(SystemMessage):
    """
    ChannelRenamedSystemMessage()

    Represents a "channel renamed" system message in group channels.

    Attributes:
        new_name:
            The new name of the channel.
        actor_id:
            The ID of the user who renamed the channel.
    """

    new_name: str = field("name")
    actor_id: int = field("by")


@final
class ChannelDescriptionChangedSystemMessage(SystemMessage):
    """
    ChannelDescriptionChangedSystemMessage()

    Represents a "channel description changed" system message in group channels.

    Attributes:
        actor_id:
            The ID of the user who changed the description of the channel.
    """

    actor_id: int = field("by")


@final
class ChannelIconChangedSystemMessage(SystemMessage):
    """
    ChannelIconChangedSystemMessage()

    Represents a "channel icon changed" system message in group channels.

    Attributes:
        actor_id:
            The ID of the user who changed the icon of the channel.
    """

    actor_id: int = field("by")


SYSTEM_MESSAGE_TYPES = {
    "text": TextSystemMessage,
    "user_added": UserAddedSystemMessage,
    "user_remove": UserRemovedSystemMessage,
    "user_joined": UserJoinedSystemMessage,
    "user_left": UserLeftSystemMessage,
    "user_kicked": UserKickedSystemMessage,
    "user_banned": UserBannedSystemMessage,
    "channel_renamed": ChannelRenamedSystemMessage,
    "channel_description_changed": ChannelDescriptionChangedSystemMessage,
    "channel_icon_changed": ChannelIconChangedSystemMessage,
}


@final
class Message(StatefulResource):
    """
    Message()

    Represents a message.

    Attributes:
        id: The message ID.
        nonce: Nonce value, used to prevent double requests to create objects.
        channel_id: The ID of the channel this message was sent in.
        author_id: The ID of the user that sent this message.
        content:
            The contents of the message. This is a (potentially empty) string,
            or `None` if this is a system message.
        system_message:
            The data of a system message. `None` if this is not a system message.
        attachments: The list of attachments the message has.
        edited_at:
            An aware UTC datetime object denoting the time the message was edited at,
            or `None` if the message was never edited.
        embeds: The list of embeds the message has.
        mention_ids: The list of IDs of the users that were mentioned in this message.
        reply_ids: The list of message IDs that were replied to with this message.
    """

    id: str = field("_id")
    nonce: Optional[str] = field("nonce", default=None)
    channel_id: str = field("channel")
    author_id: str = field("author")
    content: Optional[str] = field("content", factory=True)
    system_message: Optional[SystemMessage] = field("content", factory=True)
    attachments: list[Attachment] = field("attachments", factory=True, default=[])
    edited_at: Optional[datetime.datetime] = field("edited", factory=True, default=None)
    embeds: list[Embed] = field("embeds", factory=True, default=[])
    mention_ids: list[str] = field("mentions", default_factory=list)
    reply_ids: list[str] = field("replies", default_factory=list)

    def _content_parser(self, parser_data: ParserData) -> Optional[str]:
        content = parser_data.get_field()
        return content if isinstance(content, str) else None

    def _system_message_parser(
        self, parser_data: ParserData
    ) -> Optional[SystemMessage]:
        content = parser_data.get_field()
        return (
            SystemMessage._from_dict(content) if not isinstance(content, str) else None
        )

    def _attachments_parser(self, parser_data: ParserData) -> list[Attachment]:
        return [Attachment(self._state, data) for data in parser_data.get_field()]

    def _edited_at_parser(self, parser_data: ParserData) -> Optional[datetime.datetime]:
        return parse_datetime(parser_data.get_field())

    def _embeds_parser(self, parser_data: ParserData) -> list[Embed]:
        return [Embed._from_dict(data) for data in parser_data.get_field()]
