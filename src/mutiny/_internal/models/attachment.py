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

from .bases import Model, ParserData, StatefulResource, field

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
    type: str = field("type")

    @classmethod
    def _from_dict(cls, raw_data: dict[str, Any]) -> AttachmentMetadata:
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
    width: int = field("width")
    height: int = field("height")


@final
class VideoMetadata(AttachmentMetadata):
    width: int = field("width")
    height: int = field("height")


METADATA_TYPES = {
    "File": FileMetadata,
    "Text": TextMetadata,
    "Audio": AudioMetadata,
    "Image": ImageMetadata,
    "Video": VideoMetadata,
}


@final
class Attachment(StatefulResource):
    id: str = field("_id")
    tag: AttachmentTag = field("tag", factory=True)
    size: int = field("size")
    filename: str = field("filename")
    metadata: AttachmentMetadata = field("metadata", factory=True)
    content_type: str = field("content_type")

    def _tag_parser(self, parser_data: ParserData) -> AttachmentTag:
        return AttachmentTag(parser_data.get_field())

    def _metadata_parser(self, parser_data: ParserData) -> AttachmentMetadata:
        return AttachmentMetadata._from_dict(parser_data.get_field())

    @classmethod
    def _from_raw_data(
        cls, state: State, raw_data: Optional[dict[str, Any]]
    ) -> Optional[Attachment]:
        if raw_data is None:
            return None
        return cls(state, raw_data)
