import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator


@dataclass
class ProgressReporter:
    # This flag lets callers turn progress messages off without changing call sites.
    enabled: bool = True

    def info(self, message: str) -> None:
        if self.enabled:
            # Progress is user-facing, but stderr keeps stdout available for protocols.
            print(f"[progress] {message}", file=sys.stderr)

    @contextmanager
    def step(self, message: str) -> Iterator[None]:
        if not self.enabled:
            yield
            return

        start = time.perf_counter()
        print(f"[progress] {message}...", file=sys.stderr)
        try:
            yield
        except Exception:
            # Reporting failures here gives users feedback before the error bubbles up.
            elapsed = time.perf_counter() - start
            print(f"[progress] {message} failed after {elapsed:.2f}s", file=sys.stderr)
            raise
        else:
            # Timing each step helps spot slow MCP calls during local development.
            elapsed = time.perf_counter() - start
            print(f"[progress] {message} done in {elapsed:.2f}s", file=sys.stderr)
