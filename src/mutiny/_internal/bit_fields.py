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

from typing import final

from .models.bases import BitField, bit

__all__ = (
    "Permissions",
    "Badges",
    "ServerFlags",
    "UserFlags",
)


@final
class Permissions(BitField):
    """
    Permissions()

    Represents the server permissions or channel allow/deny overrides.
    """

    __slots__ = ()

    #: Allows members to manage the channel or channels on the server.
    manage_channels = bit(1)
    #: Allows members to change the server's name, description, icon
    #: and other related information.
    manage_server = bit(2)
    #: Allows members to manage server's/channel's permissions.
    manage_permissions = bit(4)
    #: Allows members to create, edit and delete roles with a lower than theirs.
    #: Also allows them to modify role permissions on channels.
    manage_roles = bit(8)
    #: Allows members to manage emojis on the server.
    manage_customization = bit(16)
    #: Allows members to remove other members (below their top role position)
    #: from the server. Kicked members may rejoin with an invite.
    kick_members = bit(64)
    #: Allows members to permanently remove other members
    #: (below their top role position) from the server.
    ban_members = bit(128)
    #: Allows members to time out other members (below their top role position)
    #: from the server.
    timeout_members = bit(256)
    #: Allows members to assign roles to other members below their top role position.
    assign_roles = bit(512)
    #: Allows members to change their own nickname on the server.
    change_nickname = bit(1024)
    #: Allows members to change the nicknames of other members
    #: (below their top role position) on the server.
    manage_nicknames = bit(2048)
    #: Allows members to change their server avatar on the server.
    change_avatar = bit(4096)
    #: Allows members to remove the server avatar of other members on the server.
    remove_avatars = bit(8192)
    #: Allows members to view the channels they have this permission on.
    view_channels = bit(1048576)
    #: Allows members to read the past message history.
    read_message_history = bit(2097152)
    #: Allows members to send messages in the text channel.
    send_messages = bit(4194304)
    #: Allows members to delete messages sent by other members in the text channel.
    manage_messages = bit(8388608)
    #: Allows members to manage webhook entries for the text channel.
    manage_webhooks = bit(16777216)
    #: Allows members to create invites to this server/channel.
    invite_others = bit(33554432)
    #: Allows members to send custom embeds *and* show embedded content on links
    #: the user posts in the text channel.
    send_embeds = bit(67108864)
    #: Allows members to upload files in the text channel.
    upload_files = bit(134217728)
    #: Allows members to masquerade (override their actual display name/avatar
    #: with a different one) on individual messages that they send.
    masquerade = bit(268435456)
    #: Allows members to react to messages with emojis.
    react = bit(536870912)
    #: Allows members to connect to the voice channel or channels on the server.
    connect = bit(1073741824)
    #: Allows members to speak in the voice channel or channels on the server.
    speak = bit(2147483648)
    #: Allows members to share video in the voice channel or channels on the server.
    stream_video = bit(4294967296)
    #: Allows members to mute other members (below their top role position)
    #: in the voice channel.
    mute_members = bit(8589934592)
    #: Allows members to deafen other members (below their top role position)
    #: in the voice channel.
    deafen_members = bit(17179869184)
    #: Allows members to move other members (below their top role position)
    #: between the voice channels they have this permission in.
    move_members = bit(34359738368)


@final
class Badges(BitField):
    """
    Badges()

    Represents user's badges.
    """

    __slots__ = ()

    #: Developer.
    developer = bit(1)
    #: Translator.
    translator = bit(2)
    #: Supporter.
    supporter = bit(4)
    #: Responsible Disclosure.
    responsible_disclosure = bit(8)
    #: Founder.
    founder = bit(16)
    #: Platform Moderation.
    platform_moderation = bit(32)
    #: Active Supporter.
    active_supporter = bit(64)
    #: Paw.
    paw = bit(128)
    #: Early Adopter.
    early_adopter = bit(256)
    #: Reserved Relevant Joke Badge 1.
    early_adopter = bit(512)


@final
class ServerFlags(BitField):
    """
    ServerFlags()

    Represents server's flags.
    """

    __slots__ = ()

    #: Official Revolt server.
    official = bit(1)
    #: Verified community server.
    verified = bit(2)


@final
class UserFlags(BitField):
    """
    UserFlags()

    Represents user's flags.
    """

    __slots__ = ()

    #: The account is suspended.
    suspended = bit(1)
    #: The account was deleted.
    deleted = bit(2)
    #: The account is banned.
    banned = bit(4)
