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
    ATTACHMENTS = "attachments"
    AVATARS = "avatars"
    BACKGROUNDS = "backgrounds"
    BANNERS = "banners"
    ICONS = "icons"


@final
class ImageSize(Enum):
    LARGE = "Large"
    PREVIEW = "Preview"


@final
class BandcampType(Enum):
    ALBUM = "Album"
    TRACK = "Track"


@final
class TwitchType(Enum):
    CHANNEL = "Channel"
    CLIP = "Clip"
    VIDEO = "Video"


@final
class Presence(Enum):
    BUSY = "Busy"
    IDLE = "Idle"
    INVISIBLE = "Invisible"
    ONLINE = "Online"


@final
class RelationshipStatus(Enum):
    BLOCKED = "Blocked"
    BLOCKED_OTHER = "BlockedOther"
    FRIEND = "Friend"
    INCOMING = "Incoming"
    NONE = "None"
    OUTGOING = "Outgoing"
    USER = "User"

    @classmethod
    def _from_raw_data(cls, raw_data: Optional[str]) -> Optional[RelationshipStatus]:
        if raw_data is None:
            return None
        return cls(raw_data)
