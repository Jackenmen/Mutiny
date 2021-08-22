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

import asyncio
import inspect
import itertools
import sys
import traceback
from typing import Any, Coroutine, Optional, Protocol, TypeVar, get_type_hints

from ..events import Event

__all__ = ("EventHandler", "EventListener", "EventT_contra")

_T_co = TypeVar("_T_co", covariant=True)
EventT_contra = TypeVar("EventT_contra", bound=Event, contravariant=True)


class EventListener(Protocol[EventT_contra, _T_co]):
    def __call__(self, event: EventT_contra, /) -> Coroutine[Any, Any, _T_co]:
        ...


class EventHandler:
    def __init__(self) -> None:
        self.listeners: dict[type[Event], list[EventListener]] = {}

    def add_listener(
        self, listener: EventListener, *, event_cls: Optional[type[Event]] = None
    ) -> None:
        if event_cls is None:
            signature = inspect.signature(listener)
            it = iter(signature.parameters.values())
            try:
                param = next(it)
            except StopIteration:
                raise TypeError(
                    "Function does not have one required positional argument."
                )

            if param.kind not in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.VAR_POSITIONAL,
            ):
                raise TypeError(
                    "Function does not have one required positional argument."
                )

            type_hints = get_type_hints(listener)
            try:
                event_cls = type_hints[param.name]
            except KeyError:
                raise TypeError(
                    "Function does not have a type hint on its first"
                    " positional argument."
                )

            for param in it:
                if param.default is not inspect.Parameter.empty:
                    raise TypeError("Function has more than one required argument.")

        assert event_cls is not None
        if not issubclass(event_cls, Event):
            raise TypeError(
                "Type hint of first positional argument is not a subclass of Event."
            )

        listeners = self.listeners.setdefault(event_cls, [])
        listeners.append(listener)

    def dispatch(self, event: Event) -> None:
        # islice used to skip `object`
        for cls in itertools.islice(reversed(event.__class__.__mro__), 1, None):
            assert issubclass(cls, Event)
            for listener in self.listeners.get(cls, []):
                asyncio.create_task(self.call_listener(listener, event))

    async def call_listener(self, listener: EventListener, event: Event) -> None:
        try:
            await listener(event)
        except Exception:
            print(f"Ignoring exception in {event}", file=sys.stderr)
            traceback.print_exc()
