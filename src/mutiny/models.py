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
    AttachmentTag,
    AudioMetadata,
    FileMetadata,
    ImageMetadata,
    TextMetadata,
    UnknownMetadata,
    VideoMetadata,
)
from ._internal.models.channel import (
    Channel,
    DirectMessage,
    Group,
    SavedMessages,
    TextChannel,
    UnknownChannel,
    VoiceChannel,
)
from ._internal.models.embed import (
    BandcampType,
    Embed,
    EmbeddedBandcamp,
    EmbeddedImage,
    EmbeddedNone,
    EmbeddedSpecial,
    EmbeddedSpotify,
    EmbeddedTwitch,
    EmbeddedUnknown,
    EmbeddedVideo,
    EmbeddedYouTube,
    ImageEmbed,
    ImageSize,
    NoneEmbed,
    TwitchType,
    UnknownEmbed,
    WebsiteEmbed,
)
from ._internal.models.message import (
    ChannelDescriptionChangedSystemMessage,
    ChannelIconChangedSystemMessage,
    ChannelRenamedSystemMessage,
    Message,
    SystemMessage,
    TextSystemMessage,
    UnknownSystemMessage,
    UserAddedSystemMessage,
    UserBannedSystemMessage,
    UserJoinedSystemMessage,
    UserKickedSystemMessage,
    UserLeftSystemMessage,
    UserRemovedSystemMessage,
)
from ._internal.models.permissions import (
    ChannelPermissions,
    ServerPermissions,
    UserPermissions,
)
from ._internal.models.server import (
    Category,
    Member,
    Role,
    Server,
    SystemMessageChannels,
)
from ._internal.models.user import (
    Badges,
    BotInfo,
    Presence,
    Relationship,
    RelationshipStatus,
    Status,
    User,
    UserFlags,
    UserProfile,
)

__all__ = (
    # .attachment
    "Attachment",
    "AttachmentMetadata",
    "AttachmentTag",
    "AudioMetadata",
    "FileMetadata",
    "ImageMetadata",
    "TextMetadata",
    "UnknownMetadata",
    "VideoMetadata",
    # .channel
    "Channel",
    "DirectMessage",
    "Group",
    "SavedMessages",
    "TextChannel",
    "UnknownChannel",
    "VoiceChannel",
    # .embed
    "BandcampType",
    "Embed",
    "EmbeddedBandcamp",
    "EmbeddedImage",
    "EmbeddedNone",
    "EmbeddedSpecial",
    "EmbeddedSpotify",
    "EmbeddedTwitch",
    "EmbeddedUnknown",
    "EmbeddedVideo",
    "EmbeddedYouTube",
    "ImageEmbed",
    "ImageSize",
    "NoneEmbed",
    "TwitchType",
    "UnknownEmbed",
    "WebsiteEmbed",
    # .message
    "ChannelDescriptionChangedSystemMessage",
    "ChannelIconChangedSystemMessage",
    "ChannelRenamedSystemMessage",
    "Message",
    "SystemMessage",
    "TextSystemMessage",
    "UnknownSystemMessage",
    "UserAddedSystemMessage",
    "UserBannedSystemMessage",
    "UserJoinedSystemMessage",
    "UserKickedSystemMessage",
    "UserLeftSystemMessage",
    "UserRemovedSystemMessage",
    # .permissions
    "ChannelPermissions",
    "ServerPermissions",
    "UserPermissions",
    # .server
    "Category",
    "Member",
    "Role",
    "Server",
    "SystemMessageChannels",
    # .user
    "Badges",
    "BotInfo",
    "Presence",
    "Relationship",
    "RelationshipStatus",
    "Status",
    "User",
    "UserFlags",
    "UserProfile",
)
