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

    def notification(
        self, source: str, progress: float, total: float | None, message: str | None
    ) -> None:
        if not self.enabled:
            return

        if total:
            status = f"{progress:g}/{total:g}"
        else:
            status = f"{progress:g}"

        detail = f" - {message}" if message else ""
        # These updates come from MCP notifications, not local client-side timers.
        print(f"[mcp notification] {source}: {status}{detail}", file=sys.stderr)

    def server_log(self, source: str, level: str, message: object) -> None:
        if self.enabled:
            # Server log notifications are protocol events sent by the MCP server.
            print(f"[mcp log] {source} {level}: {message}", file=sys.stderr)

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
