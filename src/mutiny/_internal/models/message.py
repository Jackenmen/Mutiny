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

import datetime
from typing import Any, Optional, final

from ..utils import parse_datetime
from .attachment import Attachment
from .bases import Model, ParserData, StatefulResource, field
from .embed import Embed

__all__ = (
    "SystemMessage",
    "UnknownSystemMessage",
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
    "Message",
)


class SystemMessage(Model):
    type: str = field("type")

    @classmethod
    def _from_dict(cls, raw_data: dict[str, Any]) -> SystemMessage:
        system_message_type = raw_data["type"]
        system_message_cls = SYSTEM_MESSAGE_TYPES.get(
            system_message_type, UnknownSystemMessage
        )
        return system_message_cls(raw_data)


@final
class UnknownSystemMessage(SystemMessage):
    __slots__ = ()


@final
class TextSystemMessage(SystemMessage):
    content: str = field("content")


@final
class UserAddedSystemMessage(SystemMessage):
    target_id: int = field("id")
    actor_id: int = field("by")


@final
class UserRemovedSystemMessage(SystemMessage):
    target_id: int = field("id")
    actor_id: int = field("by")


@final
class UserJoinedSystemMessage(SystemMessage):
    user_id: str = field("id")


@final
class UserLeftSystemMessage(SystemMessage):
    user_id: str = field("id")


@final
class UserKickedSystemMessage(SystemMessage):
    target_id: str = field("id")


@final
class UserBannedSystemMessage(SystemMessage):
    target_id: str = field("id")


@final
class ChannelRenamedSystemMessage(SystemMessage):
    new_name: str = field("name")
    actor_id: int = field("by")


@final
class ChannelDescriptionChangedSystemMessage(SystemMessage):
    actor_id: int = field("by")


@final
class ChannelIconChangedSystemMessage(SystemMessage):
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
