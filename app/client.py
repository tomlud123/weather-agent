"""
HTTP client with connection pooling and retries for OpenWeatherMap requests.
"""

from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def build_session() -> requests.Session:
    """
    Create a requests.Session configured with retries and pooling.
    """
    retry = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)

    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


# Shared session for app usage
SESSION: requests.Session = build_session()


