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
from typing import Callable, Generic, Optional, TypedDict, TypeVar, Union, overload

__all__ = ("cached_slot_property", "parse_datetime")

_T = TypeVar("_T")
_S = TypeVar("_S")

_DateTimeData = TypedDict("_DateTimeData", {"$date": str})


class cached_slot_property(Generic[_T, _S]):
    __slots__ = ("attr_name", "func")

    def __init__(self, func: Callable[[_T], _S]) -> None:
        self.attr_name = f"_cs_{func.__name__}"
        self.func = func

    @overload
    def __get__(self, instance: None, owner: type[_T]) -> cached_slot_property[_T, _S]:
        ...

    @overload
    def __get__(self, instance: _T, owner: type[_T]) -> _S:
        ...

    def __get__(
        self, instance: Optional[_T], owner: type[_T]
    ) -> Union[cached_slot_property[_T, _S], _S]:
        if instance is None:
            return self

        try:
            return getattr(instance, self.attr_name)  # type: ignore[no-any-return]
        except AttributeError:
            ret = self.func(instance)
            setattr(instance, self.attr_name, ret)
            return ret


def parse_datetime(
    datetime_data: Optional[_DateTimeData],
) -> Optional[datetime.datetime]:
    if datetime_data is None:
        return None
    date_string = datetime_data["$date"].removeprefix("Z")
    dt = datetime.datetime.fromisoformat(date_string)
    return dt.astimezone(datetime.timezone.utc)
