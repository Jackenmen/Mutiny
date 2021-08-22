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

import datetime
from typing import TYPE_CHECKING, Any

from ulid import monotonic as ulid

from ...utils import cached_slot_property

if TYPE_CHECKING:
    from ...state import State

__all__ = ("Model", "ResourceMixin", "StatefulModel", "StatefulResource")


class Model:
    __slots__ = ("raw_data",)

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data


class ResourceMixin:
    # needs to be mixin with empty slots to avoid multiple bases
    # with slots in StatefulResource
    __slots__ = ()
    id: str

    @cached_slot_property
    def created_at(self) -> datetime.datetime:
        return ulid.from_str(self.id).timestamp().datetime


class StatefulModel(Model):
    __slots__ = ("_state",)

    def __init__(self, state: State, raw_data: dict[str, Any]) -> None:
        super().__init__(raw_data)
        self._state = state


class StatefulResource(StatefulModel, ResourceMixin):
    __slots__ = ("id", "_cs_created_at")
