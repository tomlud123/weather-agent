"""
Async utilities for fetching multiple cities concurrently.

This module provides an asyncio-based wrapper that delegates to the existing
sync service function using a thread pool, preserving the same parsing,
error handling, and HTTP configuration.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Iterable, List, Optional

from service import fetch_current_weather
from models import Weather


_EXECUTOR: Optional[ThreadPoolExecutor] = None


def _get_executor() -> ThreadPoolExecutor:
    global _EXECUTOR
    if _EXECUTOR is None:
        # Use a small, bounded pool; network-bound tasks benefit from modest parallelism.
        _EXECUTOR = ThreadPoolExecutor(max_workers=8, thread_name_prefix="weather-worker")
    return _EXECUTOR


async def fetch_many_cities(cities: Iterable[str]) -> List[Optional[Weather]]:
    loop = asyncio.get_running_loop()
    executor = _get_executor()

    tasks = [loop.run_in_executor(executor, fetch_current_weather, city) for city in cities]
    # Gather preserves order; results align with input cities
    results = await asyncio.gather(*tasks, return_exceptions=False)
    return list(results)


