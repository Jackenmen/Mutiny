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

from typing import Any, Optional, final

from ..bit_fields import Permissions
from .bases import Model, field

__all__ = ("PermissionOverride",)


@final
class PermissionOverride(Model):
    """
    PermissionOverride()

    Represents a role's permission override.
    """

    #: Allows members to manage the channel or channels on the server.
    manage_channels: Optional[bool] = field("", default=None)
    #: Allows members to change the server's name, description, icon
    #: and other related information.
    manage_server: Optional[bool] = field("", default=None)
    #: Allows members to manage server's/channel's permissions.
    manage_permissions: Optional[bool] = field("", default=None)
    #: Allows members to create, edit and delete roles with a lower than theirs.
    #: Also allows them to modify role permissions on channels.
    manage_roles: Optional[bool] = field("", default=None)
    #: Allows members to manage emojis on the server.
    manage_customization: Optional[bool] = field("", default=None)
    #: Allows members to remove other members (below their top role position)
    #: from the server. Kicked members may rejoin with an invite.
    kick_members: Optional[bool] = field("", default=None)
    #: Allows members to permanently remove other members
    #: (below their top role position) from the server.
    ban_members: Optional[bool] = field("", default=None)
    #: Allows members to time out other members (below their top role position)
    #: from the server.
    timeout_members: Optional[bool] = field("", default=None)
    #: Allows members to assign roles to other members below their top role position.
    assign_roles: Optional[bool] = field("", default=None)
    #: Allows members to change their own nickname on the server.
    change_nickname: Optional[bool] = field("", default=None)
    #: Allows members to change the nicknames of other members
    #: (below their top role position) on the server.
    manage_nicknames: Optional[bool] = field("", default=None)
    #: Allows members to change their server avatar on the server.
    change_avatar: Optional[bool] = field("", default=None)
    #: Allows members to remove the server avatar of other members on the server.
    remove_avatars: Optional[bool] = field("", default=None)
    #: Allows members to view the channels they have this permission on.
    view_channels: Optional[bool] = field("", default=None)
    #: Allows members to read the past message history.
    read_message_history: Optional[bool] = field("", default=None)
    #: Allows members to send messages in the text channel.
    send_messages: Optional[bool] = field("", default=None)
    #: Allows members to delete messages sent by other members in the text channel.
    manage_messages: Optional[bool] = field("", default=None)
    #: Allows members to manage webhook entries for the text channel.
    manage_webhooks: Optional[bool] = field("", default=None)
    #: Allows members to create invites to this server/channel.
    invite_others: Optional[bool] = field("", default=None)
    #: Allows members to send custom embeds *and* show embedded content on links
    #: the user posts in the text channel.
    send_embeds: Optional[bool] = field("", default=None)
    #: Allows members to upload files in the text channel.
    upload_files: Optional[bool] = field("", default=None)
    #: Allows members to masquerade (override their actual display name/avatar
    #: with a different one) on individual messages that they send.
    masquerade: Optional[bool] = field("", default=None)
    #: Allows members to react to messages with emojis.
    react: Optional[bool] = field("", default=None)
    #: Allows members to connect to the voice channel or channels on the server.
    connect: Optional[bool] = field("", default=None)
    #: Allows members to speak in the voice channel or channels on the server.
    speak: Optional[bool] = field("", default=None)
    #: Allows members to share video in the voice channel or channels on the server.
    stream_video: Optional[bool] = field("", default=None)
    #: Allows members to mute other members (below their top role position)
    #: in the voice channel.
    mute_members: Optional[bool] = field("", default=None)
    #: Allows members to deafen other members (below their top role position)
    #: in the voice channel.
    deafen_members: Optional[bool] = field("", default=None)
    #: Allows members to move other members (below their top role position)
    #: between the voice channels they have this permission in.
    move_members: Optional[bool] = field("", default=None)

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        allow = Permissions(raw_data["a"])
        deny = Permissions(raw_data["d"])
        for attr_name in self.__class__._MODEL_FIELDS:
            if getattr(allow, attr_name) is True:
                setattr(self, attr_name, True)
            elif getattr(deny, attr_name) is True:
                setattr(self, attr_name, False)
