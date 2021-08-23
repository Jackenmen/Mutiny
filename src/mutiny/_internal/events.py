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

from .models.channel import Channel
from .models.message import Message
from .models.server import Member, Role, Server
from .models.user import Relationship, RelationshipStatus, User
from .utils import cached_slot_property

if TYPE_CHECKING:
    from .state import State

__all__ = (
    "Event",
    "ErrorEvent",
    "AuthenticatedEvent",
    "PongEvent",
    "ReadyEvent",
    "MessageEvent",
    "MessageUpdateEvent",
    "MessageDeleteEvent",
    "ChannelCreateEvent",
    "ChannelUpdateEvent",
    "ChannelDeleteEvent",
    "ChannelGroupJoinEvent",
    "ChannelGroupLeaveEvent",
    "ChannelStartTypingEvent",
    "ChannelStopTypingEvent",
    "ChannelAckEvent",
    "ServerUpdateEvent",
    "ServerDeleteEvent",
    "ServerMemberUpdateEvent",
    "ServerMemberJoinEvent",
    "ServerMemberLeaveEvent",
    "ServerRoleUpdateEvent",
    "ServerRoleDeleteEvent",
    "UserUpdateEvent",
    "UserRelationshipEvent",
)


class Event:
    __slots__ = ("_state", "raw_data", "type")

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        self._state = state
        self.raw_data = raw_data
        self.type: str = raw_data["type"]

    @classmethod
    def _from_dict(cls, state: State, raw_data: dict[str, Any]) -> Event:
        event_type = raw_data["type"]
        event_cls = EVENTS.get(event_type, UnknownEvent)
        return event_cls(state, raw_data)

    async def _gateway_handle(self) -> None:
        pass


@final
class UnknownEvent(Event):
    __slots__ = ()


@final
class ErrorEvent(Event):
    __slots__ = ("error",)

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.error: str = raw_data["error"]


@final
class AuthenticatedEvent(Event):
    __slots__ = ()


@final
class PongEvent(Event):
    __slots__ = ("_cs_time",)

    @cached_slot_property
    def time(self) -> int:
        return self.raw_data["time"]


@final
class ReadyEvent(Event):
    __slots__ = ()

    async def _gateway_handle(self) -> None:
        state = self._state
        servers = state.servers = {
            raw_data["_id"]: Server(state, raw_data)
            for raw_data in self.raw_data["servers"]
        }
        state.channels = {
            raw_data["_id"]: Channel._from_dict(state, raw_data)
            for raw_data in self.raw_data["channels"]
        }
        for raw_data in self.raw_data["users"]:
            user = User(state, raw_data)
            state.users[user.id] = user
            if user.relationship_status is RelationshipStatus.USER:
                state.user = user

        for raw_data in self.raw_data["members"]:
            member = Member(state, raw_data)
            servers[member.server_id]._members[member.user_id] = member


@final
class MessageEvent(Event):
    __slots__ = ("message",)
    message: Message

    async def _gateway_handle(self) -> None:
        self.message = Message(self._state, self.raw_data)
        channel = self._state.channels[self.message.channel_id]
        channel._update_from_event(self)


@final
class MessageUpdateEvent(Event):
    __slots__ = ("_cs_data",)

    @cached_slot_property
    def data(self) -> dict[str, Any]:
        return self.raw_data["data"]


@final
class MessageDeleteEvent(Event):
    __slots__ = ("_cs_message_id", "_cs_channel_id")

    @cached_slot_property
    def message_id(self) -> str:
        return self.raw_data["id"]

    @cached_slot_property
    def channel_id(self) -> str:
        return self.raw_data["channel"]


@final
class ChannelCreateEvent(Event):
    __slots__ = ("channel_id", "channel", "server_id")
    channel: Channel

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.channel_id: str = raw_data["_id"]
        self.server_id: Optional[str] = raw_data.get("server")

    async def _gateway_handle(self) -> None:
        self.channel = Channel._from_dict(self._state, self.raw_data)
        if self.server_id is not None:
            self._state.servers[self.server_id].channel_ids.append(self.channel_id)
        self._state.channels[self.channel_id] = self.channel


@final
class ChannelUpdateEvent(Event):
    __slots__ = ("channel_id", "channel", "data", "clear")
    channel: Channel

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.channel_id: str = raw_data["id"]
        self.data: dict[str, Any] = raw_data["data"]
        self.clear: Optional[str] = raw_data.get("clear")

    async def _gateway_handle(self) -> None:
        self.channel = self._state.channels[self.channel_id]
        self.channel._update_from_event(self)


@final
class ChannelDeleteEvent(Event):
    __slots__ = ("channel_id", "channel")
    channel: Optional[Channel]

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.channel_id: str = raw_data["id"]

    async def _gateway_handle(self) -> None:
        self.channel = self._state.channels.pop(self.channel_id, None)
        server_id = getattr(self.channel, "server_id", None)
        if server_id is not None:
            self._state.servers[server_id].channel_ids.remove(self.channel_id)


@final
class ChannelGroupJoinEvent(Event):
    __slots__ = ("channel_id", "channel", "user_id")
    channel: Channel

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.channel_id: str = raw_data["id"]
        self.user_id: str = raw_data["user"]

    async def _gateway_handle(self) -> None:
        # TODO(REST): fetch channel first if we are the ones that joined
        self.channel = self._state.channels[self.channel_id]
        self.channel._update_from_event(self)


@final
class ChannelGroupLeaveEvent(Event):
    __slots__ = ("channel_id", "channel", "user_id")
    channel: Channel

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.channel_id: str = raw_data["id"]
        self.user_id: str = raw_data["user"]

    async def _gateway_handle(self) -> None:
        self.channel = self._state.channels[self.channel_id]
        self.channel._update_from_event(self)
        if self.user_id == self._state.user.id:
            del self._state.channels[self.channel_id]


@final
class ChannelStartTypingEvent(Event):
    __slots__ = ("_cs_channel_id", "_cs_channel")

    @cached_slot_property
    def channel_id(self) -> str:
        return self.raw_data["id"]

    @cached_slot_property
    def channel(self) -> Channel:
        return self._state.channels[self.channel_id]


@final
class ChannelStopTypingEvent(Event):
    __slots__ = ("_cs_channel_id", "_cs_channel")

    @cached_slot_property
    def channel_id(self) -> str:
        return self.raw_data["id"]

    @cached_slot_property
    def channel(self) -> Channel:
        return self._state.channels[self.channel_id]


@final
class ChannelAckEvent(Event):
    __slots__ = (
        "_cs_channel_id",
        "_cs_channel",
        "_cs_user_id",
        "_cs_message_id",
    )

    @cached_slot_property
    def channel_id(self) -> str:
        return self.raw_data["id"]

    @cached_slot_property
    def channel(self) -> Channel:
        return self._state.channels[self.channel_id]

    @cached_slot_property
    def user_id(self) -> str:
        return self.raw_data["user"]

    @cached_slot_property
    def message_id(self) -> str:
        return self.raw_data["message_id"]


@final
class ServerUpdateEvent(Event):
    __slots__ = ("server_id", "server", "data", "clear")
    server: Server

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id: str = raw_data["id"]
        self.data: dict[str, Any] = raw_data["data"]
        self.clear: Optional[str] = raw_data.get("clear")

    async def _gateway_handle(self) -> None:
        self.server = self._state.servers[self.server_id]
        self.server._update_from_event(self)


@final
class ServerDeleteEvent(Event):
    __slots__ = ("server_id", "server")
    server: Server

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id: str = raw_data["id"]

    async def _gateway_handle(self) -> None:
        self.server = self._state.servers.pop(self.server_id)


@final
class ServerMemberUpdateEvent(Event):
    __slots__ = ("server_id", "server", "user_id", "data", "clear")
    server: Server

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id: str = raw_data["id"]["server"]
        self.user_id: str = raw_data["id"]["user"]
        self.data: dict[str, Any] = raw_data["data"]
        self.clear: Optional[str] = raw_data.get("clear")

    async def _gateway_handle(self) -> None:
        self.server = self._state.servers[self.server_id]
        member = self.server._members.get(self.user_id)
        if member is not None:
            member._update_from_event(self)


@final
class ServerMemberJoinEvent(Event):
    __slots__ = ("server_id", "user_id", "member")
    member: Member

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id: str = raw_data["id"]
        self.user_id: str = raw_data["user"]

    async def _gateway_handle(self) -> None:
        # TODO(REST): fetch server first if we are the ones that joined
        # note: above might get resolved by https://github.com/revoltchat/delta/pull/44
        server = self._state.servers[self.server_id]
        self.member = server._members[self.user_id] = Member(
            self._state, {"_id": {"server": self.server_id, "user": self.user_id}}
        )


@final
class ServerMemberLeaveEvent(Event):
    __slots__ = ("server_id", "server", "user_id")
    server: Server

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id: str = raw_data["id"]
        self.user_id: str = raw_data["user"]

    async def _gateway_handle(self) -> None:
        self.server = self._state.servers[self.server_id]
        self.server._members.pop(self.user_id, None)
        if self.user_id == self._state.user.id:
            del self._state.servers[self.server_id]


@final
class ServerRoleUpdateEvent(Event):
    __slots__ = ("server_id", "server", "role_id", "role", "data", "clear")
    server: Server
    role: Role

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id: str = raw_data["id"]
        self.role_id: str = raw_data["role_id"]
        self.data: dict[str, Any] = raw_data["data"]
        self.clear: Optional[str] = raw_data.get("clear")

    async def _gateway_handle(self) -> None:
        self.server = self._state.servers[self.server_id]
        try:
            role = self.server.roles[self.role_id]
        except KeyError:
            role = self.server.roles[self.role_id] = Role(self._state, self.data)
        else:
            role._update_from_event(self)
        self.role = role


@final
class ServerRoleDeleteEvent(Event):
    __slots__ = ("server_id", "server", "role_id", "role")
    server: Server
    role: Role

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id: str = raw_data["id"]
        self.role_id: str = raw_data["role_id"]

    async def _gateway_handle(self) -> None:
        self.server = self._state.servers[self.server_id]
        self.role = self.server.roles.pop(self.role_id)


@final
class UserUpdateEvent(Event):
    __slots__ = ("user_id", "user", "data", "clear")

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.user_id: str = raw_data["id"]
        self.data: dict[str, Any] = raw_data["data"]
        self.clear: Optional[str] = raw_data.get("clear")

    async def _gateway_handle(self) -> None:
        user = self._state.users.get(self.user_id)
        if user is None:
            return
        user._update_from_event(self)


@final
class UserRelationshipEvent(Event):
    __slots__ = ("self_id", "user_id", "status")

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.self_id: str = raw_data["id"]
        self.user_id: str = raw_data["user"]["_id"]
        self.status = RelationshipStatus(raw_data["status"])

    async def _gateway_handle(self) -> None:
        user = self._state.users.get(self.user_id)
        if self.status is RelationshipStatus.NONE:
            if self._state.user.relations is not None:
                self._state.user.relations.pop(self.user_id, None)
        else:
            assert self._state.user.relations is not None
            self._state.user.relations[self.user_id] = Relationship(
                self._state, {"_id": self.user_id, "status": self.status}
            )
        if user is not None:
            user.relationship_status = self.status


EVENTS = {
    "Error": ErrorEvent,
    "Authenticated": AuthenticatedEvent,
    "Pong": PongEvent,
    "Ready": ReadyEvent,
    "Message": MessageEvent,
    "MessageUpdate": MessageUpdateEvent,
    "MessageDelete": MessageDeleteEvent,
    "ChannelCreate": ChannelCreateEvent,
    "ChannelUpdate": ChannelUpdateEvent,
    "ChannelDelete": ChannelDeleteEvent,
    "ChannelGroupJoin": ChannelGroupJoinEvent,
    "ChannelGroupLeave": ChannelGroupLeaveEvent,
    "ChannelStartTyping": ChannelStartTypingEvent,
    "ChannelStopTyping": ChannelStopTypingEvent,
    "ChannelAck": ChannelAckEvent,
    "ServerUpdate": ServerUpdateEvent,
    "ServerDelete": ServerDeleteEvent,
    "ServerMemberUpdate": ServerMemberUpdateEvent,
    "ServerMemberJoin": ServerMemberJoinEvent,
    "ServerMemberLeave": ServerMemberLeaveEvent,
    "ServerRoleUpdate": ServerRoleUpdateEvent,
    "ServerRoleDelete": ServerRoleDeleteEvent,
    "UserUpdate": UserUpdateEvent,
    "UserRelationship": UserRelationshipEvent,
}
