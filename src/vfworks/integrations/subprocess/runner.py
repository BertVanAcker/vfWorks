"""Run scheduler-callable actions in isolated Python subprocesses."""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from dataclasses import dataclass, field
from typing import Any, Mapping

from vfworks.actions.contracts import JSONValue, _copy_json_value
from vfworks.actions.exceptions import InvalidActionInput
from vfworks.actions.registry import ActionDefinition


@dataclass(frozen=True, slots=True)
class SubprocessActionSpec:
    """Trusted import-path configuration for a subprocess action call."""

    action_path: str
    request_type_path: str
    result_type_path: str
    dependency_factory_path: str | None = None
    dependency_config: Mapping[str, JSONValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_import_path(self.action_path, "action_path")
        _validate_import_path(self.request_type_path, "request_type_path")
        _validate_import_path(self.result_type_path, "result_type_path")
        if self.dependency_factory_path is not None:
            _validate_import_path(self.dependency_factory_path, "dependency_factory_path")
        copied = _copy_json_value(dict(self.dependency_config), "dependency_config")
        object.__setattr__(self, "dependency_config", copied)

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "action_path": self.action_path,
            "request_type_path": self.request_type_path,
            "result_type_path": self.result_type_path,
            "dependency_factory_path": self.dependency_factory_path,
            "dependency_config": dict(self.dependency_config),
        }

    @classmethod
    def from_action_definition(
        cls,
        definition: ActionDefinition,
        *,
        dependency_factory_path: str | None = None,
        dependency_config: Mapping[str, JSONValue] | None = None,
    ) -> "SubprocessActionSpec":
        return cls(
            action_path=definition.callable_path,
            request_type_path=definition.request_type_path,
            result_type_path=definition.result_type_path,
            dependency_factory_path=dependency_factory_path,
            dependency_config=dependency_config or {},
        )


@dataclass(frozen=True, slots=True)
class SubprocessActionResult:
    """Outcome of a subprocess action invocation."""

    succeeded: bool
    result_payload: Mapping[str, JSONValue] | None = None
    exception_type: str | None = None
    message: str | None = None
    details: Mapping[str, JSONValue] = field(default_factory=dict)
    retryable: bool = False
    returncode: int | None = None
    stderr: str = ""


def run_action(
    spec: SubprocessActionSpec,
    request_payload: Mapping[str, JSONValue],
    *,
    timeout_seconds: float | None = None,
) -> SubprocessActionResult:
    """Run one configured action in a fresh Python interpreter."""

    payload = {
        "spec": spec.to_dict(),
        "request_payload": _copy_json_value(dict(request_payload), "request_payload"),
    }
    try:
        completed = subprocess.run(
            [sys.executable, "-c", _CHILD_SCRIPT],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        return SubprocessActionResult(
            succeeded=False,
            exception_type="TimeoutExpired",
            message=str(error),
            retryable=True,
            stderr=error.stderr or "",
        )

    if not completed.stdout.strip():
        return SubprocessActionResult(
            succeeded=False,
            exception_type="WorkerProtocolError",
            message="worker produced no JSON result",
            returncode=completed.returncode,
            stderr=completed.stderr,
        )

    try:
        decoded = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        return SubprocessActionResult(
            succeeded=False,
            exception_type="WorkerProtocolError",
            message=f"worker produced invalid JSON: {error}",
            returncode=completed.returncode,
            stderr=completed.stderr,
        )

    result_payload = decoded.get("result_payload")
    if result_payload is not None and not isinstance(result_payload, Mapping):
        return SubprocessActionResult(
            succeeded=False,
            exception_type="WorkerProtocolError",
            message="worker result payload must be a mapping",
            returncode=completed.returncode,
            stderr=completed.stderr,
        )

    return SubprocessActionResult(
        succeeded=bool(decoded.get("succeeded")),
        result_payload=result_payload,
        exception_type=decoded.get("exception_type"),
        message=decoded.get("message"),
        retryable=bool(decoded.get("retryable", False)),
        details=decoded.get("details", {}),
        returncode=completed.returncode,
        stderr=completed.stderr,
    )


def _validate_import_path(value: str, field_name: str) -> None:
    if not isinstance(value, str) or "." not in value or not value.strip():
        raise InvalidActionInput(f"{field_name} must be a dotted import path")


_CHILD_SCRIPT = textwrap.dedent(
    """
    import importlib
    import json
    import sys
    import traceback

    from vfworks.actions import VFWorksActionError


    def import_symbol(path):
        module_name, symbol_name = path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, symbol_name)


    def main():
        payload = json.loads(sys.stdin.read())
        spec = payload["spec"]
        request_type = import_symbol(spec["request_type_path"])
        result_type = import_symbol(spec["result_type_path"])
        action = import_symbol(spec["action_path"])
        dependencies = {}
        if spec.get("dependency_factory_path"):
            dependency_factory = import_symbol(spec["dependency_factory_path"])
            dependencies = dependency_factory(spec.get("dependency_config", {}))
        request = request_type.from_dict(payload["request_payload"])
        result = action(request, **dependencies)
        if not isinstance(result, result_type):
            raise TypeError(
                f"action returned {type(result).__name__}, expected {result_type.__name__}"
            )
        print(json.dumps({"succeeded": True, "result_payload": result.to_dict()}))


    try:
        main()
    except VFWorksActionError as error:
        traceback.print_exc(file=sys.stderr)
        print(
            json.dumps(
                {
                    "succeeded": False,
                    "exception_type": type(error).__name__,
                    "message": str(error),
                    "details": dict(error.details),
                    "retryable": bool(error.retryable),
                }
            )
        )
        sys.exit(1)
    except Exception as error:
        traceback.print_exc(file=sys.stderr)
        print(
            json.dumps(
                {
                    "succeeded": False,
                    "exception_type": type(error).__name__,
                    "message": str(error),
                    "retryable": False,
                }
            )
        )
        sys.exit(1)
    """
)
