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
from typing import TYPE_CHECKING, Any, Optional, final

from .bases import Model, StatefulResource

if TYPE_CHECKING:
    from ..state import State

__all__ = (
    "AttachmentTag",
    "AttachmentMetadata",
    "UnknownMetadata",
    "FileMetadata",
    "TextMetadata",
    "AudioMetadata",
    "ImageMetadata",
    "VideoMetadata",
    "Attachment",
)


@final
class AttachmentTag(Enum):
    ATTACHMENTS = "attachments"
    AVATARS = "avatars"
    BACKGROUNDS = "backgrounds"
    BANNERS = "banners"
    ICONS = "icons"


class AttachmentMetadata(Model):
    __slots__ = ("type",)

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.type = raw_data["type"]

    def _from_dict(self, raw_data: dict[str, Any]) -> AttachmentMetadata:
        metadata_type = raw_data["type"]
        metadata_cls = METADATA_TYPES.get(metadata_type, UnknownMetadata)
        return metadata_cls(raw_data)


@final
class UnknownMetadata(AttachmentMetadata):
    __slots__ = ()


@final
class FileMetadata(AttachmentMetadata):
    __slots__ = ()


@final
class TextMetadata(AttachmentMetadata):
    __slots__ = ()


@final
class AudioMetadata(AttachmentMetadata):
    __slots__ = ()


@final
class ImageMetadata(AttachmentMetadata):
    __slots__ = ("width", "height")

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.width = raw_data["width"]
        self.height = raw_data["height"]


@final
class VideoMetadata(AttachmentMetadata):
    __slots__ = ("width", "height")

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.width = raw_data["width"]
        self.height = raw_data["height"]


METADATA_TYPES = {
    "File": FileMetadata,
    "Text": TextMetadata,
    "Audio": AudioMetadata,
    "Image": ImageMetadata,
    "Video": VideoMetadata,
}


@final
class Attachment(StatefulResource):
    __slots__ = ("tag", "size", "filename", "metadata", "content_type")

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(state, raw_data)
        self.id: str = raw_data["_id"]
        self.tag = AttachmentTag(raw_data["tag"])
        self.size: int = raw_data["size"]
        self.filename: str = raw_data["filename"]
        self.metadata = AttachmentMetadata(raw_data["metadata"])
        self.content_type: str = raw_data["content_type"]

    @classmethod
    def _from_raw_data(
        cls, state: State, raw_data: Optional[dict[str, Any]]
    ) -> Optional[Attachment]:
        if raw_data is None:
            return None
        return cls(state, raw_data)
