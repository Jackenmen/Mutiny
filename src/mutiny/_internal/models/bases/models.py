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
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar, Union

from ulid import monotonic as ulid

from ...utils import cached_slot_property

if TYPE_CHECKING:
    from ...state import State

__all__ = (
    "InitFieldMissing",
    "UpdateFieldMissing",
    "ParserData",
    "field",
    "Model",
    "ResourceMixin",
    "StatefulModel",
    "StatefulResource",
)

_ModelMetaT = TypeVar("_ModelMetaT", bound="_ModelMeta")


class InitFieldMissing(Exception):
    __slots__ = ("keys",)

    def __init__(self, keys: tuple[Union[str, int], ...]) -> None:
        self.keys = keys
        super().__init__(f"Missing required field: {'.'.join(map(str, keys))}")


class UpdateFieldMissing(Exception):
    __slots__ = ("keys",)

    def __init__(self, keys: tuple[Union[str, int], ...]) -> None:
        self.keys = keys


class ParserData:
    __slots__ = ("model", "partial_data", "init", "keys", "default", "default_factory")

    def __init__(
        self,
        *,
        model: Model,
        partial_data: dict[str, Any],
        init: bool,
        keys: tuple[Union[str, int], ...] = None,
        default: Any = ...,
        default_factory: Optional[Callable[[], Any]] = None,
    ) -> None:
        self.model = model
        self.partial_data = partial_data
        self.init = init
        self.keys = keys
        self.default = default
        self.default_factory = default_factory

    def get_default(self) -> Any:
        if self.default is not ...:
            return self.default
        if self.default_factory is not None:
            return self.default_factory()
        return ...

    def get_field(
        self,
        /,
        *,
        keys: Optional[tuple[Union[str, int], ...]] = None,
        default: Any = ...,
    ) -> Any:
        if keys is None:
            keys = self.keys
            if keys is None:
                raise RuntimeError("There is no key given for this field!")
        assert isinstance(keys[0], str)
        try:
            it = iter(keys)
            next(it)
            value = top_value = self.partial_data[keys[0]]
            for key in it:
                value = value[key]
        except KeyError:
            if not self.init:
                raise UpdateFieldMissing(keys)
            if default is ...:
                default = self.get_default()
            if default is not ...:
                return default
            raise InitFieldMissing(keys)
        if not self.init:
            self.model.raw_data[keys[0]] = top_value
        return value


class _ModelField:
    __slots__ = ("_keys", "_factory", "_default", "_default_factory", "_parser")

    def __init__(
        self,
        key: Optional[str],
        *,
        keys: tuple[Union[str, int], ...],
        factory: bool,
        default: Any,
        default_factory: Optional[Callable[[], Any]],
    ) -> None:
        if key is not None and keys:
            raise TypeError("`key` and `keys` can't both be passed!")
        if key is not None:
            keys = (key,)
        if not factory and keys is None:
            raise TypeError("`key`, `keys`, and `factory` can't all be empty!")
        if default is not ... and default_factory is not None:
            raise TypeError("`default` and `default_factory` can't both be passed!")
        self._keys = keys
        self._factory = factory
        self._default = default
        self._default_factory = default_factory

    def __set_name__(self, owner: type, name: str) -> None:
        if type(owner) is not _ModelMeta:
            raise TypeError("field(...) can only be used on a Model class.")

    def get_value(
        self,
        model: Model,
        attr_name: str,
        partial_data: dict[str, Any],
        *,
        init: bool,
    ) -> Any:
        parser_data = ParserData(
            model=model,
            partial_data=partial_data,
            init=init,
            keys=self._keys,
            default=self._default,
            default_factory=self._default_factory,
        )
        if self._factory:
            factory: Callable[[ParserData], Any] = getattr(
                model, f"_{attr_name}_parser"
            )
            return factory(parser_data)
        return parser_data.get_field()


def field(
    key: Optional[str] = None,
    *,
    keys: tuple[Union[str, int], ...] = (),
    factory: bool = False,
    default: Any = ...,
    default_factory: Optional[Callable[[], Any]] = None,
) -> Any:
    return _ModelField(
        key,
        keys=keys,
        factory=factory,
        default=default,
        default_factory=default_factory,
    )


class _ModelMeta(type):
    _MODEL_FIELDS: dict[str, _ModelField]

    def __new__(
        cls: type[_ModelMetaT],
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, Any],
    ) -> _ModelMetaT:
        slots = set(attrs.pop("__slots__", ()))
        generated_cls = super().__new__(cls, name, bases, attrs)

        fields: dict[str, _ModelField] = {}
        for base in reversed(generated_cls.__mro__):
            base_fields: Optional[dict[str, _ModelField]] = base.__dict__.get(
                "_MODEL_FIELDS"
            )
            if base_fields is not None:
                fields.update(base_fields)
                continue
            # narrow down to annotated variables as an optimization
            base_annotations = base.__dict__.get("__annotations__", {})
            for attr_name, value in base.__dict__.items():
                if attr_name in fields:
                    del fields[attr_name]
                if attr_name in base_annotations and isinstance(value, _ModelField):
                    fields[attr_name] = value

        attrs["_MODEL_FIELDS"] = fields
        for attr_name, field in fields.items():
            if field._factory and not hasattr(generated_cls, f"_{attr_name}_parser"):
                raise TypeError(
                    f"{attr_name} is defined with factory=True"
                    " but parser for it is not defined on the class."
                )
            slots.add(attr_name)
            attrs.pop(attr_name, None)

        if attrs.get("_EMPTY_SLOTS_", False):
            attrs["__slots__"] = ()
        else:
            attrs["__slots__"] = tuple(slots)
        return super().__new__(cls, name, bases, attrs)


class Model(metaclass=_ModelMeta):
    __slots__ = ("raw_data",)

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data
        self._update_from_dict(raw_data, init=True)

    def _update_from_dict(
        self, partial_data: dict[str, Any], *, init: bool = False
    ) -> None:
        for attr_name, field in self.__class__._MODEL_FIELDS.items():
            try:
                setattr(
                    self,
                    attr_name,
                    field.get_value(self, attr_name, partial_data, init=init),
                )
            except UpdateFieldMissing:
                pass


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
        self._state = state
        super().__init__(raw_data)


class StatefulResource(StatefulModel, ResourceMixin):
    __slots__ = ("id", "_cs_created_at")
