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

import logging
from typing import TYPE_CHECKING, Any, Optional, final

from .errors import AuthenticationError, InvalidCredentials, OnboardingNotFinished
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

_log = logging.getLogger(__name__)


class Event:
    """
    Event()

    Base class for all event classes.
    """

    __slots__ = ("_state", "raw_data", "type")

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        self._state = state
        #: dict[str, Any]: The raw model data, as returned by the API.
        self.raw_data = raw_data
        #: The type of the attachment.
        #:
        #: .. note::
        #:
        #:     Checking using ``type()`` or :func:`isinstance()` should be
        #:     preferred over using this attribute.
        self.type: str = raw_data["type"]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} raw_data={self.raw_data!r}>"

    @classmethod
    def _from_dict(cls, state: State, raw_data: dict[str, Any]) -> Event:
        event_type = raw_data["type"]
        event_cls = EVENTS.get(event_type, _UnknownEvent)
        return event_cls(state, raw_data)

    async def _gateway_handle(self) -> None:
        pass


@final
class _UnknownEvent(Event):
    __slots__ = ()

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} type={self.type} raw_data={self.raw_data!r}>"
        )


@final
class ErrorEvent(Event):
    """
    ErrorEvent()

    An error occurred which meant that the client could not authenticate.

    Attributes:
        error: A raw error id (type).
    """

    __slots__ = ("error",)
    error: str

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.error = raw_data["error"]

    async def _gateway_handle(self) -> None:
        if self.error == "AlreadyAuthenticated":
            _log.warning("The client tried to authenticate for the second time.")
            return
        if self._state.gateway.authenticated:
            # it's too late to raise an exception and have it propagate to
            # the entrypoint
            _log.error("Received error event: %s", self.error)
            return
        if self.error == "InvalidSession":
            raise InvalidCredentials(
                "Failed to authenticate with the given credentials."
            )
        if self.error == "OnboardingNotFinished":
            raise OnboardingNotFinished(
                "You need to choose a username before you can connect to the gateway."
            )
        raise AuthenticationError(
            f"Received an error while trying to authenticate: {self.error}"
        )


@final
class AuthenticatedEvent(Event):
    """
    AuthenticatedEvent()

    The Authenticated event. This indicates that server has authenticated
    your connection and you will shortly start receiving data.
    """

    __slots__ = ()

    async def _gateway_handle(self) -> None:
        self._state.gateway.authenticated = True


@final
class ReadyEvent(Event):
    """
    ReadyEvent()

    The event sent by the server after authentication. This is handled by the gateway
    and should generally not be listened to.
    """

    __slots__ = ()

    async def _gateway_handle(self) -> None:
        # this needs to properly handle a READY after reconnecting
        state = self._state

        old_members: dict[str, dict[str, Member]] = {}
        servers = {}
        for raw_data in self.raw_data["servers"]:
            server_id = raw_data["_id"]
            server = state.servers.get(server_id)
            if server is None:
                server = Server(state, raw_data)
            else:
                server._update_from_dict(raw_data)
                old_members[server_id] = server._members
                server._members = {}
            servers[server_id] = server
        state.servers = servers

        channels = {}
        for raw_data in self.raw_data["channels"]:
            channel_id = raw_data["_id"]
            channel = state.channels.get(channel_id)
            if channel is None:
                channel = Channel._from_dict(state, raw_data)
            else:
                channel._update_from_dict(raw_data)
            channels[channel_id] = channel
        state.channels = channels

        users = {}
        for raw_data in self.raw_data["users"]:
            user_id = raw_data["_id"]
            user = state.users.get(user_id)
            if user is None:
                user = User(state, raw_data)
            else:
                user._update_from_dict(raw_data)
            users[user_id] = user
            if user.relationship_status is RelationshipStatus.USER:
                state.user = user
        state.users = users

        for raw_data in self.raw_data["members"]:
            server_id = raw_data["_id"]["server"]
            user_id = raw_data["_id"]["user"]
            member = old_members.get(server_id, {}).get(user_id)
            if member is None:
                member = Member(state, raw_data)
            else:
                member._update_from_dict(raw_data)
            servers[member.server_id]._members[member.id] = member
        state.ready.set()


@final
class MessageEvent(Event):
    """
    MessageEvent()

    The event sent when a message is received.

    Attributes:
        message: The received message.
    """

    __slots__ = ("message",)
    message: Message

    async def _gateway_handle(self) -> None:
        self.message = Message(self._state, self.raw_data)
        channel = self._state.channels[self.message.channel_id]
        channel._update_from_event(self)


@final
class MessageUpdateEvent(Event):
    """
    MessageUpdateEvent()

    The event sent when a message is edited or otherwise updated.
    """

    __slots__ = ("_cs_data",)

    @cached_slot_property
    def data(self) -> dict[str, Any]:
        """
        A raw partial message dictionary containing the changed fields of the message.
        """
        return self.raw_data["data"]


@final
class MessageDeleteEvent(Event):
    """
    MessageDeleteEvent()

    The event sent when a message has been deleted.
    """

    __slots__ = ("_cs_message_id", "_cs_channel_id")

    @cached_slot_property
    def message_id(self) -> str:
        """The ID of the deleted message."""
        return self.raw_data["id"]

    @cached_slot_property
    def channel_id(self) -> str:
        """The ID of the channel the deleted message was sent in."""
        return self.raw_data["channel"]


@final
class ChannelCreateEvent(Event):
    """
    ChannelCreateEvent()

    The event sent when a channel is created.

    Attributes:
        channel_id: The ID of the created channel.
        server_id: The ID of the server this channel was created in, if any.
        channel: The created channel.
    """

    __slots__ = ("channel_id", "channel", "server_id")
    channel_id: str
    channel: Channel
    server_id: Optional[str]

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.channel_id = raw_data["_id"]
        self.server_id = raw_data.get("server")

    async def _gateway_handle(self) -> None:
        self.channel = Channel._from_dict(self._state, self.raw_data)
        if self.server_id is not None:
            self._state.servers[self.server_id].channel_ids.append(self.channel_id)
        self._state.channels[self.channel_id] = self.channel


@final
class ChannelUpdateEvent(Event):
    """
    ChannelUpdateEvent()

    The event sent when the channel details are updated.

    Attributes:
        channel_id: The ID of the updated channel.
        channel: The updated channel.
        data:
            A raw partial channel dictionary containing the changed fields
            of the channel.
        clear:
            A raw string containing the name of the cleared field on the channel,
            if any.
    """

    __slots__ = ("channel_id", "channel", "data", "clear")
    channel_id: str
    channel: Channel
    data: dict[str, Any]
    clear: Optional[str]

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.channel_id = raw_data["id"]
        self.data = raw_data["data"]
        self.clear = raw_data.get("clear")

    async def _gateway_handle(self) -> None:
        self.channel = self._state.channels[self.channel_id]
        self.channel._update_from_event(self)


@final
class ChannelDeleteEvent(Event):
    """
    ChannelDeleteEvent()

    The event sent when the channel has been deleted.

    Attributes:
        channel_id: The ID of the deleted channel.
        channel: The deleted channel.
    """

    __slots__ = ("channel_id", "channel")
    channel_id: str
    channel: Optional[Channel]

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.channel_id = raw_data["id"]

    async def _gateway_handle(self) -> None:
        self.channel = self._state.channels.pop(self.channel_id, None)
        server_id = getattr(self.channel, "server_id", None)
        if server_id is not None:
            self._state.servers[server_id].channel_ids.remove(self.channel_id)


@final
class ChannelGroupJoinEvent(Event):
    """
    ChannelGroupJoinEvent()

    The event sent when a user has joined a group channel.

    Attributes:
        channel_id: The ID of the channel.
        channel: The channel.
        user_id: The ID of the user that joined the channel.
    """

    __slots__ = ("channel_id", "channel", "user_id")
    channel_id: str
    channel: Channel
    user_id: str

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.channel_id = raw_data["id"]
        self.user_id = raw_data["user"]

    async def _gateway_handle(self) -> None:
        # TODO(REST): fetch channel first if we are the ones that joined
        self.channel = self._state.channels[self.channel_id]
        self.channel._update_from_event(self)


@final
class ChannelGroupLeaveEvent(Event):
    """
    ChannelGroupLeaveEvent()

    The event sent when a user has left a group channel.

    Attributes:
        channel_id: The ID of the channel.
        channel: The channel.
        user_id: The ID of the user that left the channel.
    """

    __slots__ = ("channel_id", "channel", "user_id")
    channel_id: str
    channel: Channel
    user_id: str

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.channel_id = raw_data["id"]
        self.user_id = raw_data["user"]

    async def _gateway_handle(self) -> None:
        self.channel = self._state.channels[self.channel_id]
        self.channel._update_from_event(self)
        if self.user_id == self._state.user.id:
            del self._state.channels[self.channel_id]


@final
class ChannelStartTypingEvent(Event):
    """
    ChannelStartTypingEvent()

    The event sent when a user has started typing in a channel.
    """

    __slots__ = ("_cs_channel_id", "_cs_channel")

    @cached_slot_property
    def channel_id(self) -> str:
        """The ID of the channel."""
        return self.raw_data["id"]

    @cached_slot_property
    def channel(self) -> Channel:
        """The channel."""
        return self._state.channels[self.channel_id]


@final
class ChannelStopTypingEvent(Event):
    """
    ChannelStopTypingEvent()

    The event sent when a user has stopped typing in a channel.
    """

    __slots__ = ("_cs_channel_id", "_cs_channel")

    @cached_slot_property
    def channel_id(self) -> str:
        """The ID of the channel."""
        return self.raw_data["id"]

    @cached_slot_property
    def channel(self) -> Channel:
        """The channel."""
        return self._state.channels[self.channel_id]


@final
class ChannelAckEvent(Event):
    """
    ChannelAckEvent()

    The event sent when the client user has acknowledged new messages in a channel
    up to the given message ID.
    """

    __slots__ = (
        "_cs_channel_id",
        "_cs_channel",
        "_cs_user_id",
        "_cs_message_id",
    )

    @cached_slot_property
    def channel_id(self) -> str:
        """The ID of the channel."""
        return self.raw_data["id"]

    @cached_slot_property
    def channel(self) -> Channel:
        """The channel."""
        return self._state.channels[self.channel_id]

    @cached_slot_property
    def user_id(self) -> str:
        """The ID of the client user."""
        return self.raw_data["user"]

    @cached_slot_property
    def message_id(self) -> str:
        """The ID of the last acknowledged message."""
        return self.raw_data["message_id"]


@final
class ServerUpdateEvent(Event):
    """
    ServerUpdateEvent()

    The event sent when the server details are updated.

    Attributes:
        server_id: The ID of the updated server.
        server: The updated server.
        data:
            A raw partial server dictionary containing the changed fields
            of the server.
        clear:
            A raw string containing the name of the cleared field on the server,
            if any.
    """

    __slots__ = ("server_id", "server", "data", "clear")
    server_id: str
    server: Server
    data: dict[str, Any]
    clear: Optional[str]

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id = raw_data["id"]
        self.data = raw_data["data"]
        self.clear = raw_data.get("clear")

    async def _gateway_handle(self) -> None:
        self.server = self._state.servers[self.server_id]
        self.server._update_from_event(self)


@final
class ServerDeleteEvent(Event):
    """
    ServerDeleteEvent()

    The event sent when the server has been deleted.

    Attributes:
        server_id: The ID of the deleted server.
        server: The deleted server.
    """

    __slots__ = ("server_id", "server")
    server_id: str
    server: Server

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id = raw_data["id"]

    async def _gateway_handle(self) -> None:
        self.server = self._state.servers.pop(self.server_id)


@final
class ServerMemberUpdateEvent(Event):
    """
    ServerMemberUpdateEvent()

    The event sent when the server member details are updated.

    Attributes:
        server_id: The ID of the updated member's server.
        server: The updated member's server.
        user_id: The ID of the updated member.
        data:
            A raw partial member dictionary containing the changed fields
            of the member.
        clear:
            A raw string containing the name of the cleared field on the member,
            if any.
    """

    __slots__ = ("server_id", "server", "user_id", "data", "clear")
    server_id: str
    server: Server
    user_id: str
    data: dict[str, Any]
    clear: Optional[str]

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id = raw_data["id"]["server"]
        self.user_id = raw_data["id"]["user"]
        self.data = raw_data["data"]
        self.clear = raw_data.get("clear")

    async def _gateway_handle(self) -> None:
        self.server = self._state.servers[self.server_id]
        member = self.server._members.get(self.user_id)
        if member is not None:
            member._update_from_event(self)


@final
class ServerMemberJoinEvent(Event):
    """
    ServerMemberJoinEvent()

    The event sent when a user joins a server.

    Attributes:
        server_id: The ID of the joined server.
        server: The joined server.
        user_id: The ID of the user that joined the server.
        member: The member object for the newly joined user.
    """

    __slots__ = ("server_id", "server", "user_id", "member")
    server_id: str
    server: Server
    user_id: str
    member: Member

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id = raw_data["id"]
        self.user_id = raw_data["user"]

    async def _gateway_handle(self) -> None:
        # TODO(REST): fetch server first if we are the ones that joined
        # note: above might get resolved by https://github.com/revoltchat/delta/pull/44
        self.server = self._state.servers[self.server_id]
        self.member = self.server._members[self.user_id] = Member(
            self._state, {"_id": {"server": self.server_id, "user": self.user_id}}
        )


@final
class ServerMemberLeaveEvent(Event):
    """
    ServerMemberLeaveEvent()

    The event sent when a user leaves a server.

    Attributes:
        server_id: The ID of the server.
        server: The server.
        user_id: The ID of the user that left the server.
        member: The member object for the user that left the server, if one was cached.
    """

    __slots__ = ("server_id", "server", "user_id", "member")
    server_id: str
    server: Server
    user_id: str
    member: Optional[Member]

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id = raw_data["id"]
        self.user_id = raw_data["user"]

    async def _gateway_handle(self) -> None:
        self.server = self._state.servers[self.server_id]
        self.member = self.server._members.pop(self.user_id, None)
        if self.user_id == self._state.user.id:
            del self._state.servers[self.server_id]


@final
class ServerRoleUpdateEvent(Event):
    """
    ServerRoleUpdateEvent()

    The event sent when a server role has been updated or created.

    Attributes:
        server_id: The ID of the server.
        server: The server.
        role_id: The ID of the created/updated role.
        role: The created/updated role.
        data:
            A raw partial role dictionary containing the changed fields
            of the role.
        clear:
            A raw string containing the name of the cleared field on the role,
            if any.
        new: Whether this is a newly created role.
    """

    __slots__ = ("server_id", "server", "role_id", "role", "data", "clear", "new")
    server_id: str
    server: Server
    role_id: str
    role: Role
    data: dict[str, Any]
    clear: Optional[str]
    new: bool

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id = raw_data["id"]
        self.role_id = raw_data["role_id"]
        self.data = raw_data["data"]
        self.clear = raw_data.get("clear")

    async def _gateway_handle(self) -> None:
        self.server = self._state.servers[self.server_id]
        try:
            role = self.server.roles[self.role_id]
        except KeyError:
            self.new = True
            role = self.server.roles[self.role_id] = Role(self._state, self.data)
        else:
            self.new = False
            role._update_from_event(self)
        self.role = role


@final
class ServerRoleDeleteEvent(Event):
    """
    ServerRoleDeleteEvent()

    The event sent when a server role has been deleted.

    Attributes:
        server_id: The ID of the server.
        server: The server.
        role_id: The ID of the deleted role.
        role: The deleted role.
    """

    __slots__ = ("server_id", "server", "role_id", "role")
    server_id: str
    server: Server
    role_id: str
    role: Role

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.server_id = raw_data["id"]
        self.role_id = raw_data["role_id"]

    async def _gateway_handle(self) -> None:
        self.server = self._state.servers[self.server_id]
        self.role = self.server.roles.pop(self.role_id)


@final
class UserUpdateEvent(Event):
    """
    UserUpdateEvent()

    The event sent when a user has been updated.

    Attributes:
        user_id: The ID of the updated user.
        data:
            A raw partial user dictionary containing the changed fields
            of the user.
        clear:
            A raw string containing the name of the cleared field on the user,
            if any.
    """

    __slots__ = ("user_id", "data", "clear")
    user_id: str
    data: dict[str, Any]
    clear: Optional[str]

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.user_id = raw_data["id"]
        self.data = raw_data["data"]
        self.clear = raw_data.get("clear")

    async def _gateway_handle(self) -> None:
        user = self._state.users.get(self.user_id)
        if user is None:
            return
        user._update_from_event(self)


@final
class UserRelationshipEvent(Event):
    """
    UserRelationshipEvent()

    The event sent when the client user's relationship with another user has changed.

    Attributes:
        self_id: The ID of the client user.
        user_id: The ID of the other user with whom the relationship has changed.
        status: The new relationship status.
    """

    __slots__ = ("self_id", "user_id", "status")
    self_id: str
    user_id: str
    status: RelationshipStatus

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.self_id = raw_data["id"]
        self.user_id = raw_data["user"]["_id"]
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
