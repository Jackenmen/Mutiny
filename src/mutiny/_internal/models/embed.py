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

"""Message embeds models"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, TypeVar, final

from ..enums import BandcampType, ImageSize, LightspeedType, TwitchType
from .attachment import Attachment
from .bases import Model, ParserData, StatefulModel, field

if TYPE_CHECKING:
    from ..state import State

__all__ = (
    "Embed",
    "NoneEmbed",
    "WebsiteEmbed",
    "ImageEmbed",
    "TextEmbed",
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


class EmbeddedSpecial(Model):
    """
    EmbeddedSpecial()

    Base class for all embed special classes.

    Attributes:
        type:
            The type of the embed special.

            .. note::

                Checking using ``type()`` or :func:`isinstance()` should be
                preferred over using this attribute.
    """

    type: str = field("type")

    @classmethod
    def _from_dict(cls, raw_data: dict[str, Any]) -> Optional[EmbeddedSpecial]:
        embedded_type = raw_data["type"]
        if embedded_type == "None":
            return None
        embedded_cls = EMBEDDED_SPECIAL_TYPES.get(embedded_type, _EmbeddedUnknown)
        return embedded_cls(raw_data)

    @classmethod
    def _from_raw_data(
        cls, raw_data: Optional[dict[str, Any]]
    ) -> Optional[EmbeddedSpecial]:
        if raw_data is None:
            return None
        return cls._from_dict(raw_data)


@final
class _EmbeddedUnknown(EmbeddedSpecial):
    __slots__ = ()


@final
class EmbeddedGIF(EmbeddedSpecial):
    """
    EmbeddedGIF()

    Represents a special GIF embed.
    """


@final
class EmbeddedYouTube(EmbeddedSpecial):
    """
    EmbeddedYouTube()

    Represents a special YouTube embed.

    Attributes:
        id: The ID of the resource this embed points to.
        timestamp: The timestamp in the video this embed's link points to.
    """

    id: str = field("id")
    timestamp: Optional[str] = field("timestamp", default=None)


@final
class EmbeddedLightspeed(EmbeddedSpecial):
    """
    EmbeddedLightspeed()

    Represents a special Lightspeed.tv embed.

    Attributes:
        id: The ID of the resource this embed points to.
        content_type: The type of the resource this embed points to.
    """

    id: str = field("id")
    content_type: LightspeedType = field("content_type", factory=True)

    def _content_type_parser(self, parser_data: ParserData) -> LightspeedType:
        return LightspeedType(parser_data.get_field())


@final
class EmbeddedTwitch(EmbeddedSpecial):
    """
    EmbeddedTwitch()

    Represents a special Twitch embed.

    Attributes:
        id: The ID of the resource this embed points to.
        content_type: The type of the resource this embed points to.
    """

    id: str = field("id")
    content_type: TwitchType = field("content_type", factory=True)

    def _content_type_parser(self, parser_data: ParserData) -> TwitchType:
        return TwitchType(parser_data.get_field())


@final
class EmbeddedSpotify(EmbeddedSpecial):
    """
    EmbeddedSpotify()

    Represents a special Spotify embed.

    Attributes:
        id: The ID of the resource this embed points to.
        content_type: The type of the resource this embed points to.
    """

    id: str = field("id")
    content_type: str = field("content_type")


@final
class EmbeddedSoundcloud(EmbeddedSpecial):
    """
    EmbeddedSoundcloud()

    Represents a special Soundcloud embed.
    """

    __slots__ = ()


@final
class EmbeddedBandcamp(EmbeddedSpecial):
    """
    EmbeddedBandcamp()

    Represents a special Bandcamp embed.

    Attributes:
        id: The ID of the resource this embed points to.
        content_type: The type of the resource this embed points to.
    """

    id: str = field("id")
    content_type: BandcampType = field("content_type", factory=True)

    def _content_type_parser(self, parser_data: ParserData) -> BandcampType:
        return BandcampType(parser_data.get_field())


EMBEDDED_SPECIAL_TYPES = {
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


@final
class EmbeddedImage(_EmbeddedImageMixin):
    """
    EmbeddedImage()

    Represents a website embed image.

    Attributes:
        url: The image's URL.
        width: The image's width.
        height: The image's height.
        size: The image's size (in bytes).
    """

    __slots__ = ("url", "width", "height", "size")


@final
class EmbeddedVideo(Model):
    """
    EmbeddedVideo()

    Represents a website embed video.

    Attributes:
        url: The video's URL.
        width: The video's width.
        height: The video's height.
    """

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


class Embed(StatefulModel):
    """
    Embed()

    Base class for all embeds.

    Attributes:
        type:
            The type of the embed.

            .. note::

                Checking using ``type()`` or :func:`isinstance()` should be
                preferred over using this attribute.
    """

    type: str = field("type")

    @classmethod
    def _from_dict(cls, state: State, raw_data: dict[str, Any]) -> Embed:
        embed_type = raw_data["type"]
        embed_cls = EMBED_TYPES.get(embed_type, _UnknownEmbed)
        return embed_cls(state, raw_data)


@final
class _UnknownEmbed(Embed):
    __slots__ = ()


@final
class NoneEmbed(Embed):
    """
    NoneEmbed()

    Represents a none embed which is an embed indicating
    that there is no embed for the first URL in the message content.
    """

    __slots__ = ()


@final
class WebsiteEmbed(Embed):
    """
    WebsiteEmbed()

    Represents a website embed.

    Attributes:
        url: The website URL if provided.
        original_url: The original direct URL if provided.
        special: Special information about this website if provided.
        title: The website title if provided.
        description: The website description if provided.
        image: The website's embedded image if provided.
        video: The website's embedded video if provided.
        site_name: The website's site name if provided.
        icon_url: The website's icon URL if provided.
        colour: The website's embed colour if provided.
    """

    url: Optional[str] = field("url", default=None)
    original_url: Optional[str] = field("original_url", default=None)
    special: Optional[EmbeddedSpecial] = field("special", factory=True, default=None)
    title: Optional[str] = field("title", default=None)
    description: Optional[str] = field("description", default=None)
    image: Optional[EmbeddedImage] = field("image", factory=True, default=None)
    video: Optional[EmbeddedVideo] = field("video", factory=True, default=None)
    site_name: Optional[str] = field("site_name", default=None)
    icon_url: Optional[str] = field("icon_url", default=None)
    # XXX: maybe convert this to a consistent value
    colour: Optional[str] = field("colour", default=None)

    def _special_parser(self, parser_data: ParserData) -> Optional[EmbeddedSpecial]:
        return EmbeddedSpecial._from_raw_data(parser_data.get_field())

    def _image_parser(self, parser_data: ParserData) -> Optional[EmbeddedImage]:
        return EmbeddedImage._from_raw_data(parser_data.get_field())

    def _video_parser(self, parser_data: ParserData) -> Optional[EmbeddedVideo]:
        return EmbeddedVideo._from_raw_data(parser_data.get_field())


@final
class ImageEmbed(_EmbeddedImageMixin, Embed):
    """
    ImageEmbed()

    Represents an image embed.

    Attributes:
        url: The image's URL.
        width: The image's width.
        height: The image's height.
        size: The image's size (in bytes).
    """

    __slots__ = ()


@final
class TextEmbed(Embed):
    """
    TextEmbed()

    Represents a custom text embed.

    Attributes:
        icon_url: The icon URL if provided.
        url: The URL if provided.
        title: The title if provided.
        description: The description if provided.
        media: The embedded attachment if provided.
        colour: The embed colour if provided.
    """

    icon_url: Optional[str] = field("icon_url", default=None)
    url: Optional[str] = field("url", default=None)
    title: Optional[str] = field("title", default=None)
    description: Optional[str] = field("description", default=None)
    media: Optional[Attachment] = field("media", default=None)
    colour: Optional[str] = field("colour", default=None)

    def _attachment_parser(self, parser_data: ParserData) -> Optional[Attachment]:
        return Attachment._from_raw_data(self._state, parser_data.get_field())


EMBED_TYPES = {
    "None": NoneEmbed,
    "Website": WebsiteEmbed,
    "Image": ImageEmbed,
    "Text": TextEmbed,
}
