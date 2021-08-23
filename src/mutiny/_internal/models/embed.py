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
from typing import Any, Optional, TypeVar, final

from .bases import Model, ParserData, field

__all__ = (
    "ImageSize",
    "TwitchType",
    "BandcampType",
    "EmbeddedSpecial",
    "EmbeddedUnknown",
    "EmbeddedNone",
    "EmbeddedYouTube",
    "EmbeddedTwitch",
    "EmbeddedSpotify",
    "EmbeddedBandcamp",
    "EmbeddedImage",
    "EmbeddedVideo",
    "Embed",
    "UnknownEmbed",
    "NoneEmbed",
    "WebsiteEmbed",
    "ImageEmbed",
)


class ImageSize(Enum):
    LARGE = "Large"
    PREVIEW = "Preview"


class TwitchType(Enum):
    CHANNEL = "Channel"
    CLIP = "Clip"
    VIDEO = "Video"


class BandcampType(Enum):
    ALBUM = "Album"
    TRACK = "Track"


class EmbeddedSpecial(Model):
    type: str = field("type")

    @classmethod
    def _from_dict(cls, raw_data: dict[str, Any]) -> EmbeddedSpecial:
        embedded_type = raw_data["type"]
        embedded_cls = EMBEDDED_SPECIAL_TYPES.get(embedded_type, EmbeddedUnknown)
        return embedded_cls(raw_data)

    @classmethod
    def _from_raw_data(
        cls, raw_data: Optional[dict[str, Any]]
    ) -> Optional[EmbeddedSpecial]:
        if raw_data is None:
            return None
        return cls._from_dict(raw_data)


@final
class EmbeddedUnknown(EmbeddedSpecial):
    __slots__ = ()


@final
class EmbeddedNone(EmbeddedSpecial):
    __slots__ = ()


@final
class EmbeddedYouTube(EmbeddedSpecial):
    id: str = field("id")


@final
class EmbeddedTwitch(EmbeddedSpecial):
    id: str = field("id")
    content_type: TwitchType = field("content_type", factory=True)

    def _content_type_parser(self, parser_data: ParserData) -> TwitchType:
        return TwitchType(parser_data.get_field())


@final
class EmbeddedSpotify(EmbeddedSpecial):
    id: str = field("id")
    content_type: str = field("content_type")


@final
class EmbeddedSoundcloud(EmbeddedSpecial):
    __slots__ = ()


@final
class EmbeddedBandcamp(EmbeddedSpecial):
    id: str = field("id")
    content_type: BandcampType = field("content_type", factory=True)

    def _content_type_parser(self, parser_data: ParserData) -> BandcampType:
        return BandcampType(parser_data.get_field())


EMBEDDED_SPECIAL_TYPES = {
    "None": EmbeddedNone,
    "YouTube": EmbeddedYouTube,
    "Twitch": EmbeddedTwitch,
    "Spotify": EmbeddedSpotify,
    "Soundcloud": EmbeddedSoundcloud,
    "Bandcamp": EmbeddedBandcamp,
}


_EmbeddedImageMixinT = TypeVar("_EmbeddedImageMixinT", bound="_EmbeddedImageMixin")


class _EmbeddedImageMixin(Model):
    # This mixin needs to have empty slots to avoid multiple bases
    # with slots in ImageEmbed
    _EMPTY_SLOTS_ = True
    url: str = field("url")
    width: int = field("width")
    height: int = field("height")
    size: ImageSize = field("size", factory=True)

    def _size_parser(self, parser_data: ParserData) -> ImageSize:
        return ImageSize(parser_data.get_field())

    @classmethod
    def _from_raw_data(
        cls: type[_EmbeddedImageMixinT], raw_data: Optional[dict[str, Any]]
    ) -> Optional[_EmbeddedImageMixinT]:
        if raw_data is None:
            return None
        return cls(raw_data)


class EmbeddedImage(_EmbeddedImageMixin):
    __slots__ = ("url", "width", "height", "size")


@final
class EmbeddedVideo(Model):
    url: str = field("url")
    width: int = field("width")
    height: int = field("height")

    @classmethod
    def _from_raw_data(
        cls, raw_data: Optional[dict[str, Any]]
    ) -> Optional[EmbeddedVideo]:
        if raw_data is None:
            return None
        return cls(raw_data)


class Embed(Model):
    type: str = field("type")

    @classmethod
    def _from_dict(cls, raw_data: dict[str, Any]) -> Embed:
        embed_type = raw_data["type"]
        embed_cls = EMBED_TYPES.get(embed_type, UnknownEmbed)
        return embed_cls(raw_data)


@final
class UnknownEmbed(Embed):
    __slots__ = ()


@final
class NoneEmbed(Embed):
    __slots__ = ()


@final
class WebsiteEmbed(Embed):
    url: Optional[str] = field("url", default=None)
    special: Optional[EmbeddedSpecial] = field("special", factory=True, default=None)
    title: Optional[str] = field("title", default=None)
    description: Optional[str] = field("description", default=None)
    image: Optional[EmbeddedImage] = field("image", factory=True, default=None)
    video: Optional[EmbeddedVideo] = field("video", factory=True, default=None)
    site_name: Optional[str] = field("site_name", default=None)
    icon_url: Optional[str] = field("icon_url", default=None)
    # XXX: maybe convert this to a consistent value
    colour: Optional[str] = field("color", default=None)

    def _special_parser(self, parser_data: ParserData) -> Optional[EmbeddedSpecial]:
        return EmbeddedSpecial._from_raw_data(parser_data.get_field())

    def _image_parser(self, parser_data: ParserData) -> Optional[EmbeddedImage]:
        return EmbeddedImage._from_raw_data(parser_data.get_field())

    def _video_parser(self, parser_data: ParserData) -> Optional[EmbeddedVideo]:
        return EmbeddedVideo._from_raw_data(parser_data.get_field())


@final
class ImageEmbed(_EmbeddedImageMixin, Embed):
    __slots__ = ()


EMBED_TYPES = {
    "None": NoneEmbed,
    "Website": WebsiteEmbed,
    "Image": ImageEmbed,
}
