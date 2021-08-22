from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine, Generator
from typing import Any, Generic, Optional, TypeVar, Union, final

from ...utils import cached_slot_property
from .models import Model

_T_co = TypeVar("_T_co", covariant=True)


_ModelT = TypeVar("_ModelT", bound=Model)
_ModelS = TypeVar("_ModelS", bound=Model)


@final
class CachableModel(Awaitable[_ModelS], Generic[_ModelT, _ModelS]):
    __slots__ = ("_instance", "_func")

    def __init__(
        self,
        instance: _ModelT,
        getter: Callable[[_ModelT], Optional[_ModelS]],
        fetcher: Callable[[_ModelT], Coroutine[Any, Any, _ModelS]],
    ) -> None:
        self._instance = instance
        self._getter = getter
        self._fetcher = fetcher

    @cached_slot_property
    def cached(self) -> Optional[_ModelS]:
        return self._getter(self._instance)

    def __await__(self) -> Generator[Any, None, _ModelS]:
        return self._get_or_fetch().__await__()

    async def _get_or_fetch(self) -> _ModelS:
        cached = self.cached
        if cached is not None:
            return cached
        return await self.fetch()

    async def fetch(self) -> _ModelS:
        return await self._fetcher(self._instance)


class cachable_model(Generic[_ModelT, _ModelS]):
    def __init__(self, getter: Callable[[_ModelT], Optional[_ModelS]]) -> None:
        self._getter = getter
        self._fetcher: Optional[
            Callable[[_ModelT], Coroutine[Any, Any, _ModelS]]
        ] = None

    def fetcher(
        self, fetcher: Callable[[_ModelT], Coroutine[Any, Any, _ModelS]]
    ) -> cachable_model[_ModelT, _ModelS]:
        self._fetcher = fetcher
        return self

    def __get__(
        self, instance: Optional[_ModelT], owner: type[_ModelT]
    ) -> Union[CachableModel[_ModelT, _ModelS], cachable_model[_ModelT, _ModelS]]:
        if instance is None:
            return self
        if self._fetcher is None:
            raise TypeError("Cachable model does not have a fetcher defined!")
        return CachableModel(instance, self._getter, self._fetcher)
