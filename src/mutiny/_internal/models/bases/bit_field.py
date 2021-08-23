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

from typing import Optional, Union, final, overload

__all__ = ("BitField", "bit")


class BitField:
    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} value={self.value}>"


@final
class bit:
    __slots__ = ("bit_value", "name")
    name: str

    def __init__(self, bit_value: int) -> None:
        self.bit_value = bit_value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name!r} value={self.bit_value}>"

    def __set_name__(self, owner: type[BitField], name: str) -> None:
        self.name = name

    @overload
    def __get__(self, instance: BitField, owner: type[BitField]) -> bool:
        ...

    @overload
    def __get__(self, instance: None, owner: type[BitField]) -> bit:
        ...

    def __get__(
        self, instance: Optional[BitField], owner: type[BitField]
    ) -> Union[bit, bool]:
        if instance is None:
            return self

        return (instance.value & self.bit_value) == self.bit_value
