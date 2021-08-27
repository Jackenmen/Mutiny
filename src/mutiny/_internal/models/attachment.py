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

"""Attachment models"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, final

from ..enums import AttachmentTag
from .bases import Model, ParserData, StatefulResource, field

if TYPE_CHECKING:
    from ..state import State

__all__ = (
    "AttachmentMetadata",
    "FileMetadata",
    "TextMetadata",
    "AudioMetadata",
    "ImageMetadata",
    "VideoMetadata",
    "Attachment",
)


class AttachmentMetadata(Model):
    """
    AttachmentMetadata()

    Base class for all attachment metadata classes.

    Attributes:
        type:
            The type of the attachment.

            .. note::

                Checking using ``type()`` or :func:`isinstance()` should be
                preferred over using this attribute.
    """

    type: str = field("type")

    @classmethod
    def _from_dict(cls, raw_data: dict[str, Any]) -> AttachmentMetadata:
        metadata_type = raw_data["type"]
        metadata_cls = METADATA_TYPES.get(metadata_type, _UnknownMetadata)
        return metadata_cls(raw_data)


@final
class _UnknownMetadata(AttachmentMetadata):
    __slots__ = ()


@final
class FileMetadata(AttachmentMetadata):
    """
    FileMetadata()

    Represents the attachment metadata of a file.
    """

    __slots__ = ()


@final
class TextMetadata(AttachmentMetadata):
    """
    TextMetadata()

    Represents the attachment metadata of a text file.
    """

    __slots__ = ()


@final
class AudioMetadata(AttachmentMetadata):
    """
    AudioMetadata()

    Represents the attachment metadata of an audio file.
    """

    __slots__ = ()


@final
class ImageMetadata(AttachmentMetadata):
    """
    ImageMetadata()

    Represents the attachment metadata of a image file.

    Attributes:
        width: The image width.
        height: The image height.
    """

    width: int = field("width")
    height: int = field("height")


@final
class VideoMetadata(AttachmentMetadata):
    """
    VideoMetadata()

    Represents the attachment metadata of a video file.

    Attributes:
        width: The video width.
        height: The video height.
    """

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
    """
    Attachment()

    Represents an attachment.

    Attributes:
        id: The attachment ID.
        tag: The attachment tag.
        size: The file size (in bytes).
        filename: The file name.
        metadata: The attachment metadata.
        content_type: The file's content type.
    """

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
