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

from typing import Any, Optional, TypeVar, final

from .bases import Model

__all__ = (
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


class EmbeddedSpecial(Model):
    __slots__ = ("type",)

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.type: str = raw_data["type"]

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
    __slots__ = ("id",)

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.id: str = raw_data["id"]


@final
class EmbeddedTwitch(EmbeddedSpecial):
    __slots__ = ("content_type", "id")

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        # XXX: This is Enum: "Channel" "Clip" "Video"
        self.content_type: str = raw_data["content_type"]
        self.id: str = raw_data["id"]


@final
class EmbeddedSpotify(EmbeddedSpecial):
    __slots__ = ("content_type", "id")

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.content_type: str = raw_data["content_type"]
        self.id: str = raw_data["id"]


@final
class EmbeddedSoundcloud(EmbeddedSpecial):
    __slots__ = ()


@final
class EmbeddedBandcamp(EmbeddedSpecial):
    __slots__ = ("content_type", "id")

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        # XXX: This is Enum: "Album" "Track"
        self.content_type: str = raw_data["content_type"]
        self.id: str = raw_data["id"]


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
    __slots__ = ()

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.url: str = raw_data["url"]
        self.width: int = raw_data["width"]
        self.height: int = raw_data["height"]
        # XXX: this is Enum: "Large" "Preview"
        self.size: str = raw_data["size"]

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
    __slots__ = ("url", "width", "height")

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.url: str = raw_data["url"]
        self.width: int = raw_data["width"]
        self.height: int = raw_data["height"]

    @classmethod
    def _from_raw_data(
        cls, raw_data: Optional[dict[str, Any]]
    ) -> Optional[EmbeddedVideo]:
        if raw_data is None:
            return None
        return cls(raw_data)


class Embed(Model):
    __slots__ = ("type",)

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.type: str = raw_data["type"]

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
    __slots__ = (
        "url",
        "special",
        "title",
        "description",
        "image",
        "video",
        "site_name",
        "icon_url",
        "color",
    )

    def __init__(self, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self.url: Optional[str] = raw_data.get("url")
        self.special = EmbeddedSpecial._from_raw_data(raw_data.get("special"))
        self.title: Optional[str] = raw_data.get("title")
        self.description: Optional[str] = raw_data.get("description")
        self.image = EmbeddedImage._from_raw_data(raw_data.get("image"))
        self.video = EmbeddedVideo._from_raw_data(raw_data.get("video"))
        self.site_name: Optional[str] = raw_data.get("site_name")
        self.icon_url: Optional[str] = raw_data.get("icon_url")
        # XXX: maybe convert this to a consistent value
        self.color: Optional[str] = raw_data.get("color")


@final
class ImageEmbed(_EmbeddedImageMixin, Embed):
    __slots__ = ()


EMBED_TYPES = {
    "None": NoneEmbed,
    "Website": WebsiteEmbed,
    "Image": ImageEmbed,
}
