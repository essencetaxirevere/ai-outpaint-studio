"""A tiny in-process worker pool for batch outpainting jobs."""
from __future__ import annotations

import queue
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

from loguru import logger


@dataclass
class QueuedJob:
    source: Path
    target: str
    anchor: str = "center"
    prompt: str | None = None
    extras: dict = field(default_factory=dict)


class JobQueue:
    def __init__(self, pool_size: int = 2) -> None:
        self.pool_size = max(1, pool_size)
        self._q: queue.Queue[QueuedJob | None] = queue.Queue()
        self._threads: list[threading.Thread] = []
        self._results: dict[Path, list[Path]] = {}
        self._lock = threading.Lock()

    def start(self, handler: Callable[[QueuedJob], list[Path]]) -> None:
        def _worker() -> None:
            while True:
                item = self._q.get()
                if item is None:
                    break
                try:
                    files = handler(item)
                    with self._lock:
                        self._results[item.source] = files
                except Exception as exc:  # noqa: BLE001
                    logger.exception("worker failed on {}: {}", item.source, exc)
                finally:
                    self._q.task_done()

        for _ in range(self.pool_size):
            t = threading.Thread(target=_worker, daemon=True)
            t.start()
            self._threads.append(t)

    def submit(self, jobs: Iterable[QueuedJob]) -> None:
        for j in jobs:
            self._q.put(j)

    def join(self) -> dict[Path, list[Path]]:
        self._q.join()
        for _ in self._threads:
            self._q.put(None)
        for t in self._threads:
            t.join(timeout=5.0)
        return dict(self._results)