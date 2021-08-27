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
    "ChannelPermissions",
    "ServerPermissions",
    "Badges",
    "UserFlags",
)


@final
class ChannelPermissions(BitField):
    """
    ChannelPermissions()

    Represents the channel permissions.
    """

    __slots__ = ()

    #: Allows members to view the channel.
    view = bit(1)
    #: Allows members to send messages in the text channel.
    send_message = bit(2)
    #: Allows members to delete messages sent by other members in the text channel.
    manage_messages = bit(4)
    #: Allows members to manage the channel.
    manage_channel = bit(8)
    #: Allows members to join the voice channel.
    voice_call = bit(16)
    #: Allows members to invite other users to the channel.
    invite_others = bit(32)
    #: Allows members to show embedded content on links the user posts
    #: in the text channel.
    embed_links = bit(64)
    #: Allows members to upload files in the text channel.
    upload_files = bit(128)


@final
class ServerPermissions(BitField):
    """
    ServerPermissions()

    Represents the server permissions.
    """

    __slots__ = ()

    #: Allows members to view the channel.
    view = bit(1)
    #: Allows members to create, edit and delete roles with a lower than theirs.
    #: Also allows them to modify role permissions on channels.
    manage_roles = bit(2)
    #: Allows members to crete, edit and delete channels.
    manage_channels = bit(4)
    #: Allows members to change the server's name, description, icon
    #: and other related information.
    manage_server = bit(8)
    #: Allows members to remove members from the server.
    #: Kicked members may rejoin with an invite.
    kick_members = bit(16)
    #: Allows members to permanently remove members from the server.
    ban_members = bit(32)
    #: Allows members to change the nickname on the server.
    change_nickname = bit(4096)
    #: Allows members to change the nicknames of other members on the server.
    manage_nicknames = bit(8192)
    #: Allows members to change their server avatar on the server.
    change_avatar = bit(16382)
    #: Allows members to remove the server avatar of other members on the server.
    remove_avatars = bit(32768)


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
    #: Revolt Team.
    revolt_team = bit(16)
    #: Early Adopter.
    early_adopter = bit(256)


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
