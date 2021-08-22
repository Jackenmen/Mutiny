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

from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, final

from .attachment import Attachment
from .bases import BitField, Model, StatefulModel, StatefulResource, bit

if TYPE_CHECKING:
    from ..state import State

__all__ = (
    "Badges",
    "UserFlags",
    "RelationshipStatus",
    "Presence",
    "Status",
    "Relationship",
    "BotInfo",
    "UserProfile",
    "User",
)


@final
class Badges(BitField):
    developer = bit(1)
    translator = bit(2)
    supporter = bit(4)
    responsible_disclosure = bit(8)
    revolt_team = bit(16)
    early_adopter = bit(256)


@final
class UserFlags(BitField):
    suspended = bit(1)
    deleted = bit(2)
    banned = bit(4)


@final
class RelationshipStatus(Enum):
    BLOCKED = "Blocked"
    BLOCKED_OTHER = "BlockedOther"
    FRIEND = "Friend"
    INCOMING = "Incoming"
    NONE = "None"
    OUTGOING = "Outgoing"
    USER = "User"

    @classmethod
    def _from_raw_data(cls, raw_data: Optional[str]) -> Optional[RelationshipStatus]:
        if raw_data is None:
            return None
        return cls(raw_data)


@final
class Presence(Enum):
    BUSY = "Busy"
    IDLE = "Idle"
    INVISIBLE = "Invisible"
    ONLINE = "Online"


@final
class Status(Model):
    __slots__ = ("text", "presence")

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.text: Optional[str] = raw_data.get("text")
        # Users who have never changed their presence do not have the `presence`.
        # New users start with an Online presence,
        # so that's what we should use in such case.
        self.presence = Presence(raw_data.get("presence", "Online"))


@final
class Relationship(StatefulModel):
    __slots__ = ("_state", "raw_data", "user_id", "status")

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.user_id = raw_data["_id"]
        self.status = RelationshipStatus(raw_data["status"])

    @classmethod
    def _from_raw_data(
        cls, state: State, raw_data: Optional[dict[str, Any]]
    ) -> Optional[Relationship]:
        if raw_data is None:
            return None
        return cls(state, raw_data)


@final
class BotInfo(StatefulModel):
    __slots__ = ("owner_id",)

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.owner_id = raw_data["owner"]

    @classmethod
    def _from_raw_data(
        cls, state: State, raw_data: Optional[dict[str, Any]]
    ) -> Optional[BotInfo]:
        if raw_data is None:
            return None
        return cls(state, raw_data)


@final
class UserProfile(StatefulModel):
    __slots__ = ("content", "background")

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.content = raw_data.get("content")
        self.background = Attachment._from_raw_data(state, raw_data.get("background"))

    @classmethod
    def _from_raw_data(
        cls, state: State, raw_data: Optional[dict[str, Any]]
    ) -> Optional[UserProfile]:
        if raw_data is None:
            return None
        return cls(state, raw_data)


@final
class User(StatefulResource):
    __slots__ = (
        "username",
        "avatar",
        "relations",
        "badges",
        "status",
        "relationship_status",
        "online",
        "flags",
        "bot",
        "profile",
    )

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.id: str = raw_data["_id"]
        self.username: str = raw_data["username"]
        self.avatar = Attachment._from_raw_data(state, raw_data.get("avatar"))
        self.relations: Optional[dict[str, Relationship]] = None
        if (relations_data := raw_data.get("relations", None)) is not None:
            self.relations = {
                data["_id"]: Relationship(state, data) for data in relations_data
            }
        self.badges = Badges(raw_data.get("badges", 0))
        self.status = Status(raw_data.get("status", {}))
        self.relationship_status = RelationshipStatus._from_raw_data(
            raw_data.get("relationship")
        )
        self.online: Optional[bool] = raw_data["online"]
        self.flags = UserFlags(raw_data.get("flags", 0))
        self.bot = BotInfo._from_raw_data(state, raw_data.get("bot"))
        self.profile = UserProfile._from_raw_data(state, raw_data.get("profile"))
