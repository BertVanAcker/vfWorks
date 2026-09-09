"""Serializable value contracts shared by externally scheduled actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, TypeAlias, cast
from urllib.parse import urlparse

from vfworks.actions.exceptions import InvalidActionInput

JSONPrimitive: TypeAlias = None | bool | int | float | str
"""A scalar value supported by JSON."""

JSONValue: TypeAlias = JSONPrimitive | list["JSONValue"] | dict[str, "JSONValue"]
"""A recursively JSON-compatible value."""


def _require_non_empty_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidActionInput(f"{field_name} must be a non-empty string")
    return value


def _copy_json_value(value: Any, field_name: str) -> JSONValue:
    """Validate and detach a JSON-compatible value from caller-owned objects."""
    if value is None or isinstance(value, (bool, int, str)):
        return cast(JSONPrimitive, value)
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise InvalidActionInput(f"{field_name} must contain finite numbers")
        return value
    if isinstance(value, list):
        return [
            _copy_json_value(item, f"{field_name}[{index}]")
            for index, item in enumerate(value)
        ]
    if isinstance(value, dict):
        copied: dict[str, JSONValue] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise InvalidActionInput(f"{field_name} keys must be strings")
            copied[key] = _copy_json_value(item, f"{field_name}.{key}")
        return copied
    raise InvalidActionInput(
        f"{field_name} must contain only JSON-compatible values, "
        f"not {type(value).__name__}"
    )


def _copy_metadata(metadata: Mapping[str, JSONValue]) -> Mapping[str, JSONValue]:
    if not isinstance(metadata, Mapping):
        raise InvalidActionInput("metadata must be a mapping")
    copied = _copy_json_value(dict(metadata), "metadata")
    return MappingProxyType(cast(dict[str, JSONValue], copied))


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    """A portable reference to data stored outside scheduler task metadata.

    The URI identifies durable content available to workers. Credentials must
    not be embedded in the URI; workers obtain them from runtime configuration.
    """

    uri: str
    media_type: str
    checksum: str | None = None
    size_bytes: int | None = None
    metadata: Mapping[str, JSONValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        uri = _require_non_empty_string(self.uri, "uri")
        _require_non_empty_string(self.media_type, "media_type")
        if not urlparse(uri).scheme:
            raise InvalidActionInput("uri must include a scheme such as file: or s3:")
        if self.checksum is not None:
            _require_non_empty_string(self.checksum, "checksum")
        if (
            self.size_bytes is not None
            and (isinstance(self.size_bytes, bool) or self.size_bytes < 0)
        ):
            raise InvalidActionInput("size_bytes must be a non-negative integer")
        if self.size_bytes is not None and not isinstance(self.size_bytes, int):
            raise InvalidActionInput("size_bytes must be a non-negative integer")
        object.__setattr__(self, "metadata", _copy_metadata(self.metadata))

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a detached dictionary suitable for JSON serialization."""
        return {
            "uri": self.uri,
            "media_type": self.media_type,
            "checksum": self.checksum,
            "size_bytes": self.size_bytes,
            "metadata": cast(dict[str, JSONValue], _copy_json_value(dict(self.metadata), "metadata")),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> ArtifactRef:
        """Create a validated reference from a scheduler-decoded mapping."""
        if not isinstance(value, Mapping):
            raise InvalidActionInput("artifact reference must be a mapping")
        allowed = {"uri", "media_type", "checksum", "size_bytes", "metadata"}
        unknown = set(value) - allowed
        if unknown:
            raise InvalidActionInput(
                f"artifact reference contains unknown fields: {sorted(unknown)!r}"
            )
        try:
            return cls(
                uri=value["uri"],
                media_type=value["media_type"],
                checksum=value.get("checksum"),
                size_bytes=value.get("size_bytes"),
                metadata=value.get("metadata", {}),
            )
        except KeyError as error:
            raise InvalidActionInput(
                f"artifact reference is missing required field {error.args[0]!r}"
            ) from error


@dataclass(frozen=True, slots=True)
class ExecutionInfo:
    """Scheduler-provided identifiers used for tracing and idempotency."""

    workflow_run_id: str
    task_run_id: str
    attempt: int
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty_string(self.workflow_run_id, "workflow_run_id")
        _require_non_empty_string(self.task_run_id, "task_run_id")
        if isinstance(self.attempt, bool) or not isinstance(self.attempt, int):
            raise InvalidActionInput("attempt must be a positive integer")
        if self.attempt < 1:
            raise InvalidActionInput("attempt must be a positive integer")
        if self.correlation_id is not None:
            _require_non_empty_string(self.correlation_id, "correlation_id")

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a dictionary suitable for JSON serialization."""
        return {
            "workflow_run_id": self.workflow_run_id,
            "task_run_id": self.task_run_id,
            "attempt": self.attempt,
            "correlation_id": self.correlation_id,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> ExecutionInfo:
        """Create validated execution metadata from a decoded mapping."""
        if not isinstance(value, Mapping):
            raise InvalidActionInput("execution info must be a mapping")
        allowed = {"workflow_run_id", "task_run_id", "attempt", "correlation_id"}
        unknown = set(value) - allowed
        if unknown:
            raise InvalidActionInput(
                f"execution info contains unknown fields: {sorted(unknown)!r}"
            )
        try:
            return cls(
                workflow_run_id=value["workflow_run_id"],
                task_run_id=value["task_run_id"],
                attempt=value["attempt"],
                correlation_id=value.get("correlation_id"),
            )
        except KeyError as error:
            raise InvalidActionInput(
                f"execution info is missing required field {error.args[0]!r}"
            ) from error
