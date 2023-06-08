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

from ._internal.models.attachment import (
    Attachment,
    AttachmentMetadata,
    AudioMetadata,
    FileMetadata,
    ImageMetadata,
    TextMetadata,
    VideoMetadata,
)
from ._internal.models.channel import (
    Channel,
    DMChannel,
    GroupChannel,
    SavedMessagesChannel,
    TextChannel,
    VoiceChannel,
)
from ._internal.models.embed import (
    Embed,
    EmbeddedBandcamp,
    EmbeddedGIF,
    EmbeddedImage,
    EmbeddedLightspeed,
    EmbeddedSpecial,
    EmbeddedSpotify,
    EmbeddedTwitch,
    EmbeddedVideo,
    EmbeddedYouTube,
    ImageEmbed,
    NoneEmbed,
    TextEmbed,
    WebsiteEmbed,
)
from ._internal.models.message import (
    ChannelDescriptionChangedSystemMessage,
    ChannelIconChangedSystemMessage,
    ChannelRenamedSystemMessage,
    Masquerade,
    Message,
    SystemMessage,
    TextSystemMessage,
    UserAddedSystemMessage,
    UserBannedSystemMessage,
    UserJoinedSystemMessage,
    UserKickedSystemMessage,
    UserLeftSystemMessage,
    UserRemovedSystemMessage,
)
from ._internal.models.permission_override import PermissionOverride
from ._internal.models.server import (
    Category,
    Member,
    Role,
    Server,
    SystemMessageChannels,
)
from ._internal.models.user import BotInfo, Relationship, Status, User, UserProfile

__all__ = (
    # .user
    "User",
    "BotInfo",
    "Relationship",
    "Status",
    "UserProfile",
    # .channel
    "Channel",
    "SavedMessagesChannel",
    "DMChannel",
    "GroupChannel",
    "TextChannel",
    "VoiceChannel",
    # .message
    "Message",
    "Masquerade",
    "ChannelDescriptionChangedSystemMessage",
    "ChannelIconChangedSystemMessage",
    "ChannelRenamedSystemMessage",
    "SystemMessage",
    "TextSystemMessage",
    "UserAddedSystemMessage",
    "UserBannedSystemMessage",
    "UserJoinedSystemMessage",
    "UserKickedSystemMessage",
    "UserLeftSystemMessage",
    "UserRemovedSystemMessage",
    # .permission_override
    "PermissionOverride",
    # .server
    "Server",
    "Category",
    "Member",
    "Role",
    "SystemMessageChannels",
    # .attachment
    "Attachment",
    "AttachmentMetadata",
    "AudioMetadata",
    "FileMetadata",
    "ImageMetadata",
    "TextMetadata",
    "VideoMetadata",
    # .embed
    "Embed",
    "NoneEmbed",
    "TextEmbed",
    "WebsiteEmbed",
    "ImageEmbed",
    "EmbeddedSpecial",
    "EmbeddedGIF",
    "EmbeddedYouTube",
    "EmbeddedTwitch",
    "EmbeddedLightspeed",
    "EmbeddedSpotify",
    "EmbeddedBandcamp",
    "EmbeddedImage",
    "EmbeddedVideo",
)
