"""
Async HTTP client with connection pooling and retries for OpenWeatherMap requests.
"""

from __future__ import annotations

import asyncio
from typing import Optional

import aiohttp
from aiohttp import ClientTimeout, ClientError, ClientResponse


class AsyncWeatherClient:
    """Async HTTP client for OpenWeatherMap API with retries and connection pooling."""
    
    def __init__(self, timeout: tuple[float, float] = (3.5, 10.0)):
        self.timeout = ClientTimeout(total=timeout[1], connect=timeout[0])
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(
            limit=10,  # Total connection pool size
            limit_per_host=10,  # Per-host connection limit
        )
        self._session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout,
            headers={"Accept": "application/json"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
    
    async def get(self, url: str, params: dict) -> Optional[dict]:
        """Make GET request with retry logic."""
        if not self._session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        for attempt in range(5):  # 5 retries
            try:
                async with self._session.get(url, params=params) as response:
                    if response.status in (429, 500, 502, 503, 504):
                        # Retry on these status codes
                        if attempt < 4:  # Don't sleep on last attempt
                            await asyncio.sleep(0.5 * (2 ** attempt))  # Exponential backoff
                            continue
                    
                    response.raise_for_status()
                    return await response.json()
                    
            except (ClientError, asyncio.TimeoutError) as e:
                if attempt < 4:  # Don't sleep on last attempt
                    await asyncio.sleep(0.5 * (2 ** attempt))
                    continue
                raise e
        
        return None


# Global client instance
_client: Optional[AsyncWeatherClient] = None


async def get_client() -> AsyncWeatherClient:
    """Get or create global async client."""
    global _client
    if _client is None:
        _client = AsyncWeatherClient()
    return _client


