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

from typing import Any, ClassVar, Optional, Union, final, overload

__all__ = ("BitField", "bit")


class BitField:
    """Base class for all bit field classes."""

    __slots__ = ("value",)
    #: The mapping of the bit name to the bit value.
    BITS: ClassVar[dict[str, int]]
    #: The raw bit field value.
    value: int

    def __init__(self, value: int = 0, **kwargs: bool) -> None:
        self.value = value
        for bit_name, bit_value in kwargs.items():
            if bit_name not in self.BITS:
                raise TypeError(
                    f"{bit_name!r} is not a valid bit for {self.__class__.__name__}."
                )
            setattr(self, bit_name, bit_value)

    def __init_subclass__(cls) -> None:
        cls.BITS = {
            attr_name: attr_value.bit_value
            for base in reversed(cls.__mro__)
            for attr_name, attr_value in base.__dict__.items()
            if isinstance(attr_value, bit)
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} value={self.value}>"

    def __eq__(self, other: Any) -> bool:
        """
        Compare the bit fields for equality.

        Parameters:
            other:
                The other bit field. This bit field needs to be of the same type to
                compare equal.
        """
        return isinstance(other, self.__class__) and self.value == other.value

    def __ne__(self, other: Any) -> bool:
        """
        Compare the bit fields for inequality.

        Parameters:
            other:
                The other bit field. This bit field will also be considered unequal
                if it is not of the same type.
        """
        return not self.__eq__(other)


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

    def __set__(self, instance: BitField, value: bool) -> None:
        if value is True:
            instance.value |= self.bit_value
        elif value is False:
            instance.value &= ~self.bit_value
        else:
            raise TypeError("A bit can only be set to a bool.")
