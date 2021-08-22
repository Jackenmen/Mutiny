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

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ._internal.state import State

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
    def from_dict(cls, state: State, raw_data: dict[str, Any]) -> Event:
        event_type = raw_data["type"]
        event_cls = EVENTS.get(event_type, UnknownEvent)
        return event_cls(state, raw_data)


class UnknownEvent(Event):
    __slots__ = ()


class ErrorEvent(Event):
    __slots__ = ()


class AuthenticatedEvent(Event):
    __slots__ = ()


class PongEvent(Event):
    __slots__ = ()


class ReadyEvent(Event):
    __slots__ = ()


class MessageEvent(Event):
    __slots__ = ()


class MessageUpdateEvent(Event):
    __slots__ = ()


class MessageDeleteEvent(Event):
    __slots__ = ()


class ChannelCreateEvent(Event):
    __slots__ = ()


class ChannelUpdateEvent(Event):
    __slots__ = ()


class ChannelDeleteEvent(Event):
    __slots__ = ()


class ChannelGroupJoinEvent(Event):
    __slots__ = ()


class ChannelGroupLeaveEvent(Event):
    __slots__ = ()


class ChannelStartTypingEvent(Event):
    __slots__ = ()


class ChannelStopTypingEvent(Event):
    __slots__ = ()


class ChannelAckEvent(Event):
    __slots__ = ()


class ServerUpdateEvent(Event):
    __slots__ = ()


class ServerDeleteEvent(Event):
    __slots__ = ()


class ServerMemberUpdateEvent(Event):
    __slots__ = ()


class ServerMemberJoinEvent(Event):
    __slots__ = ()


class ServerMemberLeaveEvent(Event):
    __slots__ = ()


class ServerRoleUpdateEvent(Event):
    __slots__ = ()


class ServerRoleDeleteEvent(Event):
    __slots__ = ()


class UserUpdateEvent(Event):
    __slots__ = ()


class UserRelationshipEvent(Event):
    __slots__ = ()


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
