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

import asyncio
import logging
import random
from typing import Any, Optional, final, overload

__all__ = ("MaxAttemptsReached", "ExponentialBackoff")


class MaxAttemptsReached(Exception):
    pass


@final
class ExponentialBackoff:
    BASE = 2

    def __init__(
        self, *, max_attempts: Optional[int] = 5, max_delay: float = 64.0
    ) -> None:
        self.max_attempts = max_attempts
        self.max_delay = max_delay
        self.attempt = 0
        self.exponent = 0

    def get_delay(self) -> Optional[float]:
        if not self.attempt:
            self.attempt += 1
            return None
        if self.max_attempts is not None and self.attempt == self.max_attempts:
            raise MaxAttemptsReached
        delay = self.BASE ** self.exponent
        self.attempt += 1
        if delay >= self.max_delay:
            delay = self.max_delay
        else:
            self.exponent += 1
        return delay + random.random()

    @overload
    async def delay(self) -> float:
        ...

    @overload
    async def delay(self, log: logging.Logger, msg: str, *args: Any) -> float:
        ...

    async def delay(
        self,
        log: Optional[logging.Logger] = None,
        msg: Optional[str] = None,
        *args: Any,
    ) -> Optional[float]:
        delay = self.get_delay()
        if delay is None:
            return None
        if log is not None:
            log.info(msg, *args, delay)
        await asyncio.sleep(delay)
        return delay

    def reset(self) -> None:
        self.attempt = 0
        self.exponent = 0

    def __aiter__(self) -> ExponentialBackoff:
        return self

    async def __anext__(self) -> Optional[float]:
        try:
            return await self.delay()
        except MaxAttemptsReached:
            raise StopAsyncIteration
