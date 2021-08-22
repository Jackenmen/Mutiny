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

from ..utils import parse_datetime
from .attachment import Attachment
from .bases import Model, StatefulResource
from .embed import Embed

if TYPE_CHECKING:
    from ..state import State

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
    __slots__ = ("type",)

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.type = raw_data["type"]

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
    __slots__ = ("content",)

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.content = raw_data["content"]


@final
class UserAddedSystemMessage(SystemMessage):
    __slots__ = ("target_id", "actor_id")

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.target_id = raw_data["id"]
        self.actor_id = raw_data["by"]


@final
class UserRemovedSystemMessage(SystemMessage):
    __slots__ = ("target_id", "actor_id")

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.target_id = raw_data["id"]
        self.actor_id = raw_data["by"]


@final
class UserJoinedSystemMessage(SystemMessage):
    __slots__ = ("user_id",)

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.user_id = raw_data["id"]


@final
class UserLeftSystemMessage(SystemMessage):
    __slots__ = ("user_id",)

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.user_id = raw_data["id"]


@final
class UserKickedSystemMessage(SystemMessage):
    __slots__ = ("target_id",)

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.target_id = raw_data["id"]


@final
class UserBannedSystemMessage(SystemMessage):
    __slots__ = ("target_id",)

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.target_id = raw_data["id"]


@final
class ChannelRenamedSystemMessage(SystemMessage):
    __slots__ = ("new_name", "actor_id")

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.new_name = raw_data["name"]
        self.actor_id = raw_data["by"]


@final
class ChannelDescriptionChangedSystemMessage(SystemMessage):
    __slots__ = ("actor_id",)

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.actor_id = raw_data["by"]


@final
class ChannelIconChangedSystemMessage(SystemMessage):
    __slots__ = ("actor_id",)

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.actor_id = raw_data["by"]


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
    __slots__ = (
        "nonce",
        "channel_id",
        "author_id",
        "content",
        "system_message",
        "attachments",
        "edited_at",
        "embeds",
        "mention_ids",
        "reply_ids",
    )

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.id: str = raw_data["_id"]
        self.nonce: Optional[str] = raw_data.get("nonce")
        self.channel_id: str = raw_data["channel"]
        self.author_id: str = raw_data["author"]
        self.content: Optional[str]
        self.system_message: Optional[SystemMessage]
        content: Union[dict[str, Any], str] = raw_data["content"]
        if isinstance(content, str):
            self.content = content
            self.system_message = None
        else:
            self.content = None
            self.system_message = SystemMessage._from_dict(content)

        self.attachments = [
            Attachment(state, attachment_data)
            for attachment_data in raw_data.get("attachments", [])
        ]
        self.edited_at = parse_datetime(raw_data.get("edited"))
        self.embeds = [
            Embed._from_dict(embed_data) for embed_data in raw_data.get("embeds", [])
        ]
        self.mention_ids: list[str] = raw_data.get("mentions", [])
        self.reply_ids: list[str] = raw_data.get("replies", [])
