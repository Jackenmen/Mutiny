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

"""User models"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, final

from ..bit_fields import Badges, UserFlags
from ..enums import Presence, RelationshipStatus
from .attachment import Attachment
from .bases import Model, ParserData, StatefulModel, StatefulResource, field

if TYPE_CHECKING:
    from ...events import UserUpdateEvent
    from ..state import State

__all__ = (
    "Status",
    "Relationship",
    "BotInfo",
    "UserProfile",
    "User",
)


@final
class Status(Model):
    """
    Status()

    Represents a user's status.

    Attributes:
        text: The custom status text.
        presence: The user's presence.
    """

    text: Optional[str] = field("text", default=None)
    # Users who have never changed their presence do not have the `presence`.
    # New users start with an Online presence,
    # so that's what we should use in such case.
    presence: Presence = field("presence", factory=True, default="Online")

    def _presence_parser(self, parser_data: ParserData) -> Presence:
        return Presence(parser_data.get_field())


@final
class Relationship(StatefulModel):
    """
    Relationship()

    Represents the client user's relationship with other user.

    Attributes:
        user_id: The ID of the other user in this relation.
        status: The relationship's status.
    """

    user_id: str = field("_id")
    status: RelationshipStatus = field("status", factory=True)

    def _status_parser(self, parser_data: ParserData) -> RelationshipStatus:
        return RelationshipStatus(parser_data.get_field())


@final
class BotInfo(StatefulModel):
    """
    BotInfo()

    Represents the information about a bot user.

    Attributes:
        owner_id: The ID of the bot owner.
    """

    owner_id: str = field("owner")

    @classmethod
    def _from_raw_data(
        cls, state: State, raw_data: Optional[dict[str, Any]]
    ) -> Optional[BotInfo]:
        if raw_data is None:
            return None
        return cls(state, raw_data)


@final
class UserProfile(StatefulModel):
    """
    UserProfile()

    Represents a profile of a user.

    Attributes:
        content: The profile content if provided.
        background: The profile background if provided.
    """

    content: Optional[str] = field("content", default=None)
    background: Optional[Attachment] = field("background", factory=True, default=None)

    def _background_parser(self, parser_data: ParserData) -> Optional[Attachment]:
        return Attachment._from_raw_data(self._state, parser_data.get_field())

    @classmethod
    def _from_raw_data(
        cls, state: State, raw_data: Optional[dict[str, Any]]
    ) -> Optional[UserProfile]:
        if raw_data is None:
            return None
        return cls(state, raw_data)


@final
class User(StatefulResource):
    """
    User()

    Represents a user.

    Attributes:
        id: The user ID.
        username: The username.
        avatar: The user's avatar.
        relations: The user's relations. This is only present for the client user.
        badges: The user's badges.
        status: The user's status.
        relationship_status: The client user's relationship status with this user.
        online: Indicates whether the user is online.
        flags: The user flags.
        bot: The information about this bot, or `None` if this user is not a bot.
        profile: The user's profile.
    """

    id: str = field("_id")
    username: str = field("username")
    avatar: Optional[Attachment] = field("avatar", factory=True, default=None)
    relations: Optional[dict[str, Relationship]] = field(
        "relations", factory=True, default=None
    )
    badges: Badges = field("badges", factory=True, default=0)
    status: Status = field("status", factory=True, default_factory=dict)
    relationship_status: Optional[RelationshipStatus] = field(
        "relationship", factory=True, default=None
    )
    online: bool = field("online")
    flags: UserFlags = field("flags", factory=True, default=0)
    bot: Optional[BotInfo] = field("bot", factory=True, default=None)
    profile: Optional[UserProfile] = field("profile", factory=True, default=None)

    def _avatar_parser(self, parser_data: ParserData) -> Optional[Attachment]:
        return Attachment._from_raw_data(self._state, parser_data.get_field())

    def _relations_parser(
        self, parser_data: ParserData
    ) -> Optional[dict[str, Relationship]]:
        relations_data = parser_data.get_field()
        if relations_data is None:
            return None
        return {data["_id"]: Relationship(self._state, data) for data in relations_data}

    def _badges_parser(self, parser_data: ParserData) -> Badges:
        return Badges(parser_data.get_field())

    def _status_parser(self, parser_data: ParserData) -> Status:
        return Status(parser_data.get_field())

    def _relationship_status_parser(
        self, parser_data: ParserData
    ) -> Optional[RelationshipStatus]:
        return RelationshipStatus._from_raw_data(parser_data.get_field())

    def _flags_parser(self, parser_data: ParserData) -> UserFlags:
        return UserFlags(parser_data.get_field())

    def _bot_parser(self, parser_data: ParserData) -> Optional[BotInfo]:
        return BotInfo._from_raw_data(self._state, parser_data.get_field())

    def _profile_parser(self, parser_data: ParserData) -> Optional[UserProfile]:
        return UserProfile._from_raw_data(self._state, parser_data.get_field())

    def _update_from_event(self, event: UserUpdateEvent) -> None:
        if event.clear == "ProfileContent":
            if self.profile is not None:
                self.profile.raw_data.pop("content", None)
                self.profile.content = None
        elif event.clear == "ProfileBackground":
            if self.profile is not None:
                self.profile.raw_data.pop("background", None)
                self.profile.background = None
        elif event.clear == "StatusText":
            self.status.raw_data.pop("text", None)
            self.status.text = None
        elif event.clear == "Avatar":
            self.raw_data["avatar"] = None
            self.avatar = None
        # XXX: updates to `profile` are currently not handled
        # due to the use of dot notation
        self._update_from_dict(event.data)
