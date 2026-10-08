"""Polite HTTP downloads: declared User-Agent, rate limit, retries with backoff, disk cache."""

from __future__ import annotations

import time
from pathlib import Path

import requests

from . import config

_last_request = 0.0


def _wait_for_slot() -> None:
    """Keep every caller under the SEC limit of 5 requests per second."""
    global _last_request
    gap = 1.0 / config.SEC_MAX_REQUESTS_PER_SECOND
    wait = _last_request + gap - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    _last_request = time.monotonic()


def download(
    url: str,
    dest: Path,
    *,
    user_agent: str | None = None,
    force: bool = False,
    retries: int = 3,
    progress: bool = False,
) -> bool:
    """Stream `url` to `dest`. Returns False on a 404, True otherwise.

    An existing file is kept unless `force`. The body goes to a `.part` file first, so an
    interrupted download never looks finished.
    """
    if dest.exists() and not force:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": user_agent or "fundsponsor (github.com/Puraav/funded-and-sponsoring)"}
    part = dest.with_suffix(dest.suffix + ".part")
    for attempt in range(1, retries + 1):
        _wait_for_slot()
        try:
            with requests.get(url, headers=headers, stream=True, timeout=120) as response:
                if response.status_code == 404:
                    return False
                response.raise_for_status()
                total = int(response.headers.get("Content-Length", 0))
                done = 0
                next_report = 0.1
                with part.open("wb") as handle:
                    for chunk in response.iter_content(chunk_size=1 << 20):
                        handle.write(chunk)
                        done += len(chunk)
                        if progress and total and done / total >= next_report:
                            print(f"  {dest.name}: {done / total:.0%} of {total / 1e6:.0f} MB")
                            next_report += 0.1
            part.replace(dest)
            return True
        except requests.RequestException as error:
            if attempt == retries:
                raise
            delay = 2**attempt
            print(f"  retry {attempt}/{retries} for {url} in {delay}s ({error})")
            time.sleep(delay)
    return False
