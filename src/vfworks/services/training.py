from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Callable
from uuid import uuid4

from vfworks.examples import ExampleConfig, ExampleRuntime

CREATE_SESSION = "Create session"
RESET_SESSION = "Reset session"
CLOSE_SESSION = "Close session"


@dataclass
class _Session:
    runtime: ExampleRuntime
    invocation: int = 0


class TrainingServiceManager:
    """Execute independently requested actions; callers own all orchestration."""

    def __init__(self, config: ExampleConfig):
        self.config = config
        self._sessions: dict[str, _Session] = {}
        # The current example runtimes temporarily change process cwd.
        self._lock = RLock()
        reserved = {CREATE_SESSION, RESET_SESSION, CLOSE_SESSION}
        if reserved.intersection(self.task_names):
            raise ValueError("Example actions must not use reserved session service names")

    @property
    def task_names(self) -> tuple[str, ...]:
        return tuple(task.name for task in self.config.tasks)

    @property
    def service_names(self) -> tuple[str, ...]:
        return (CREATE_SESSION, RESET_SESSION, CLOSE_SESSION, *self.task_names)

    def execute(
        self,
        task_name: str,
        incoming: dict[str, Any],
        progress: Callable[[str, int], None] | None = None,
    ) -> dict[str, Any]:
        if task_name not in self.service_names:
            raise KeyError(f"Unknown service: {task_name}")
        with self._lock:
            if task_name == CREATE_SESSION:
                if incoming:
                    raise ValueError("Create session does not accept input artifacts")
                run_id = str(uuid4())
                session = _Session(ExampleRuntime(self.config))
                self._sessions[run_id] = session
            else:
                context = incoming.get("context")
                if not isinstance(context, dict) or not isinstance(context.get("run_id"), str):
                    raise ValueError("A context artifact with run_id is required")
                run_id = context["run_id"]
                if run_id not in self._sessions:
                    raise KeyError("Unknown or expired session")
                session = self._sessions[run_id]

            session.invocation += 1
            outcome, message = "ok", ""
            if progress:
                progress(f"Starting {task_name}", 0)
            try:
                if task_name == RESET_SESSION:
                    session.runtime = ExampleRuntime(self.config)
                elif task_name == CLOSE_SESSION:
                    del self._sessions[run_id]
                elif task_name != CREATE_SESSION:
                    with session.runtime.execution_context():
                        action = session.runtime.tasks()[task_name]
                        if action() is False:
                            outcome, message = "nok", "Action reported an unsuccessful result"
            except NotImplementedError as error:
                outcome, message = "not_implemented", str(error)
            except Exception as error:
                outcome, message = "error", f"{type(error).__name__}: {error}"
            if progress:
                progress(f"{'Finished' if outcome == 'ok' else 'Failed'} {task_name}", 100)
            return {
                "result": outcome,
                "context": {"run_id": run_id, "example": self.config.name},
                "report": {
                    "action": task_name,
                    "result": outcome,
                    "message": message,
                    "invocation": session.invocation,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            }

    def discard(self, run_id: str) -> bool:
        with self._lock:
            return self._sessions.pop(run_id, None) is not None
