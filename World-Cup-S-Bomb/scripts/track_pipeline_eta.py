"""Lightweight runtime, throughput, ETA, and peak-memory tracking."""

from __future__ import annotations

import json
import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Generator, Iterable, Iterator, TypeVar

from tqdm.auto import tqdm

T = TypeVar("T")
DEFAULT_LOG = (
    Path(__file__).resolve().parents[1] / "logs" / "pipeline_execution_eta.json"
)


@dataclass
class StageRuntime:
    """Serializable timing record for one pipeline stage."""

    name: str
    status: str
    elapsed_seconds: float
    completed: int
    total: int | None
    unit: str
    average_units_per_second: float
    eta_seconds: float | None
    peak_memory_mb: float
    message: str = ""


class PipelineTimer:
    """Track bounded stages and atomically persist their runtime summaries."""

    def __init__(self, log_path: Path = DEFAULT_LOG, pipeline: str = "production") -> None:
        self.log_path = Path(log_path)
        self.pipeline = pipeline
        self.started_at = time.perf_counter()
        self.stages: list[StageRuntime] = []
        self.previous_runs: list[dict[str, Any]] = []
        if self.log_path.exists():
            try:
                previous = json.loads(self.log_path.read_text(encoding="utf-8"))
                self.previous_runs.extend(previous.pop("previous_runs", []))
                previous.pop("active_stage", None)
                self.previous_runs.append(previous)
            except (OSError, json.JSONDecodeError):
                self.previous_runs = []
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        self._write()

    @staticmethod
    def _memory_mb() -> float:
        _, peak = tracemalloc.get_traced_memory()
        return peak / (1024 * 1024)

    def record(
        self,
        name: str,
        started: float,
        *,
        completed: int = 1,
        total: int | None = 1,
        unit: str = "stage",
        status: str = "complete",
        message: str = "",
    ) -> StageRuntime:
        """Record and persist a completed or failed stage."""

        elapsed = max(time.perf_counter() - started, 1e-9)
        speed = completed / elapsed
        remaining = None
        if total is not None and completed > 0:
            remaining = max(total - completed, 0) / speed
        runtime = StageRuntime(
            name=name,
            status=status,
            elapsed_seconds=elapsed,
            completed=int(completed),
            total=None if total is None else int(total),
            unit=unit,
            average_units_per_second=speed,
            eta_seconds=remaining,
            peak_memory_mb=self._memory_mb(),
            message=message,
        )
        self.stages.append(runtime)
        self._write()
        return runtime

    @contextmanager
    def stage(
        self,
        name: str,
        *,
        total: int | None = 1,
        unit: str = "stage",
    ) -> Generator[Callable[[int, str], None], None, None]:
        """Context manager whose callback persists live progress and ETA."""

        started = time.perf_counter()
        state = {"completed": 0, "message": ""}

        def update(completed: int, message: str = "") -> None:
            state["completed"] = completed
            state["message"] = message
            elapsed = max(time.perf_counter() - started, 1e-9)
            speed = completed / elapsed if completed else 0.0
            eta = (
                max((total or completed) - completed, 0) / speed
                if total is not None and speed > 0
                else None
            )
            live = StageRuntime(
                name=name,
                status="running",
                elapsed_seconds=elapsed,
                completed=completed,
                total=total,
                unit=unit,
                average_units_per_second=speed,
                eta_seconds=eta,
                peak_memory_mb=self._memory_mb(),
                message=message,
            )
            self._write(live)

        try:
            yield update
        except Exception as exc:
            self.record(
                name,
                started,
                completed=state["completed"],
                total=total,
                unit=unit,
                status="failed",
                message=f"{type(exc).__name__}: {exc}",
            )
            raise
        else:
            completed = state["completed"] or (total if total is not None else 1)
            self.record(
                name,
                started,
                completed=completed,
                total=total,
                unit=unit,
                message=state["message"],
            )

    def progress(
        self,
        iterable: Iterable[T],
        *,
        name: str,
        total: int | None = None,
        unit: str = "item",
    ) -> Iterator[T]:
        """Yield a tqdm-wrapped iterable while persisting live ETA updates."""

        known_total = total if total is not None else getattr(iterable, "__len__", lambda: None)()
        with self.stage(name, total=known_total, unit=unit) as update:
            for index, item in enumerate(
                tqdm(iterable, total=known_total, desc=name, unit=unit), start=1
            ):
                if index == 1 or index % 10 == 0 or index == known_total:
                    update(index)
                yield item

    def summary(self) -> dict[str, Any]:
        """Return the current serializable runtime summary."""

        return {
            "schema_version": 1,
            "pipeline": self.pipeline,
            "status": (
                "failed"
                if any(stage.status == "failed" for stage in self.stages)
                else "complete"
            ),
            "elapsed_seconds": time.perf_counter() - self.started_at,
            "peak_memory_mb": self._memory_mb(),
            "stages": [asdict(stage) for stage in self.stages],
            "previous_runs": self.previous_runs,
        }

    def _write(self, live_stage: StageRuntime | None = None) -> None:
        payload = self.summary()
        if live_stage is not None:
            payload["status"] = "running"
            payload["active_stage"] = asdict(live_stage)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.log_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.log_path)


def timed_stage(name: str | None = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorate a function that optionally receives ``timer=PipelineTimer``."""

    def decorator(function: Callable[..., T]) -> Callable[..., T]:
        @wraps(function)
        def wrapped(*args: Any, **kwargs: Any) -> T:
            timer = kwargs.get("timer")
            owned = not isinstance(timer, PipelineTimer)
            if owned:
                timer = PipelineTimer(pipeline=function.__module__)
            with timer.stage(name or function.__name__) as update:
                result = function(*args, **kwargs)
                update(1)
            return result

        return wrapped

    return decorator
