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
from typing import Optional, final

__all__ = (
    "AttachmentTag",
    "ImageSize",
    "BandcampType",
    "TwitchType",
    "Presence",
    "RelationshipStatus",
)


@final
class AttachmentTag(Enum):
    """
    AttachmentTag()

    Specifies the attachment tag/bucket used for the `mutiny.models.Attachment`
    in the CDN.
    """

    #: File uploads.
    ATTACHMENTS = "attachments"
    #: User avatars.
    AVATARS = "avatars"
    #: User profile backgrounds.
    BACKGROUNDS = "backgrounds"
    #: Banners.
    BANNERS = "banners"
    #: Channel and server icons.
    ICONS = "icons"


@final
class ImageSize(Enum):
    """
    ImageSize()

    Specifies the image size for an embedded image in `mutiny.models.EmbeddedImage`
    and `mutiny.models.ImageEmbed`.
    """

    #: This is a large image.
    LARGE = "Large"
    #: This is a preview image.
    PREVIEW = "Preview"


@final
class BandcampType(Enum):
    """
    BandcampType()

    Specifies the content type for an embedded Bandcamp URL
    in `mutiny.models.EmbeddedBandcamp`.
    """

    #: This is an embed for a Bandcamp album.
    ALBUM = "Album"
    #: This is an embed for a Bandcamp track.
    TRACK = "Track"


@final
class TwitchType(Enum):
    """
    TwitchType()

    Specifies the content type for an embedded Twitch URL
    in `mutiny.models.EmbeddedTwitch`.
    """

    #: This is an embed for a Twitch channel.
    CHANNEL = "Channel"
    #: This is an embed for a Twitch clip.
    CLIP = "Clip"
    #: This is an embed for a Twitch video.
    VIDEO = "Video"


@final
class Presence(Enum):
    """
    Presence()

    Specifies the user's presence.
    """

    #: The user is busy.
    BUSY = "Busy"
    #: The user is idle.
    IDLE = "Idle"
    #: The user is invisible.
    INVISIBLE = "Invisible"
    #: The user is online.
    ONLINE = "Online"


@final
class RelationshipStatus(Enum):
    """
    RelationshipStatus()

    Specifies the client user's relationship with the user.
    """

    #: This user is blocked by the client user.
    #:
    #: .. note:
    #:     This user might have the client user blocked too,
    #:     the API does not show any indication of that
    #:     when the client user already has the user blocked.
    BLOCKED = "Blocked"
    #: This user has the client user blocked.
    BLOCKED_OTHER = "BlockedOther"
    #: This user is the client user's friend.
    FRIEND = "Friend"
    #: This user has sent a friend request to the client user.
    INCOMING = "Incoming"
    #: This user has no relationship with the client user.
    NONE = "None"
    #: This user has a pending friend request from the client user.
    OUTGOING = "Outgoing"
    #: This is the client user.
    USER = "User"

    @classmethod
    def _from_raw_data(cls, raw_data: Optional[str]) -> Optional[RelationshipStatus]:
        if raw_data is None:
            return None
        return cls(raw_data)
