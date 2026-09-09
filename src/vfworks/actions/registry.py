"""Action discovery and contract-version metadata."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable, Mapping

from vfworks.actions.contracts import JSONValue, _require_non_empty_string
from vfworks.actions.data import collect_data, prepare_data
from vfworks.actions.exceptions import InvalidActionInput
from vfworks.actions.models import (
    CollectDataRequest,
    CollectDataResult,
    EvaluateModelRequest,
    EvaluateModelResult,
    FitModelRequest,
    FitModelResult,
    PrepareDataRequest,
    PrepareDataResult,
    evaluate_model,
    fit_model,
)

ACTION_CONTRACT_VERSION = "2026-07-23"


@dataclass(frozen=True, slots=True)
class ActionDefinition:
    """Stable scheduler-facing metadata for one action contract."""

    name: str
    version: str
    callable_path: str
    retry_safe: bool
    request_type: type
    result_type: type

    def __post_init__(self) -> None:
        _require_non_empty_string(self.name, "name")
        _require_non_empty_string(self.version, "version")
        _require_non_empty_string(self.callable_path, "callable_path")
        if "." not in self.callable_path:
            raise InvalidActionInput("callable_path must be a dotted import path")
        if not isinstance(self.retry_safe, bool):
            raise InvalidActionInput("retry_safe must be a boolean")
        if not isinstance(self.request_type, type):
            raise InvalidActionInput("request_type must be a type")
        if not isinstance(self.result_type, type):
            raise InvalidActionInput("result_type must be a type")

    @property
    def request_type_path(self) -> str:
        return _type_path(self.request_type)

    @property
    def result_type_path(self) -> str:
        return _type_path(self.result_type)

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "name": self.name,
            "version": self.version,
            "callable_path": self.callable_path,
            "retry_safe": self.retry_safe,
            "request_type_path": self.request_type_path,
            "result_type_path": self.result_type_path,
        }


class ActionRegistry:
    """Immutable lookup table for scheduler-facing action definitions."""

    def __init__(self, definitions: tuple[ActionDefinition, ...] = ()) -> None:
        by_key: dict[tuple[str, str], ActionDefinition] = {}
        latest_by_name: dict[str, ActionDefinition] = {}
        for definition in definitions:
            key = (definition.name, definition.version)
            if key in by_key:
                raise InvalidActionInput(
                    f"duplicate action registration for {definition.name!r} "
                    f"version {definition.version!r}"
                )
            by_key[key] = definition
            latest_by_name[definition.name] = definition

        self._by_key = MappingProxyType(by_key)
        self._latest_by_name = MappingProxyType(latest_by_name)

    def get(self, name: str, *, version: str | None = None) -> ActionDefinition:
        _require_non_empty_string(name, "name")
        if version is not None:
            _require_non_empty_string(version, "version")
            try:
                return self._by_key[(name, version)]
            except KeyError as error:
                raise InvalidActionInput(
                    f"unknown action {name!r} version {version!r}"
                ) from error
        try:
            return self._latest_by_name[name]
        except KeyError as error:
            raise InvalidActionInput(f"unknown action {name!r}") from error

    def require_version(self, name: str, version: str) -> ActionDefinition:
        return self.get(name, version=version)

    @property
    def definitions(self) -> tuple[ActionDefinition, ...]:
        return tuple(self._by_key.values())

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._latest_by_name)


def default_action_registry() -> ActionRegistry:
    """Return built-in action definitions without plugin discovery."""

    return ActionRegistry(
        (
            ActionDefinition(
                name="vfworks.data.collect",
                version=ACTION_CONTRACT_VERSION,
                callable_path="vfworks.actions.collect_data",
                retry_safe=True,
                request_type=CollectDataRequest,
                result_type=CollectDataResult,
            ),
            ActionDefinition(
                name="vfworks.data.prepare",
                version=ACTION_CONTRACT_VERSION,
                callable_path="vfworks.actions.prepare_data",
                retry_safe=True,
                request_type=PrepareDataRequest,
                result_type=PrepareDataResult,
            ),
            ActionDefinition(
                name="vfworks.models.fit",
                version=ACTION_CONTRACT_VERSION,
                callable_path="vfworks.actions.fit_model",
                retry_safe=True,
                request_type=FitModelRequest,
                result_type=FitModelResult,
            ),
            ActionDefinition(
                name="vfworks.models.evaluate",
                version=ACTION_CONTRACT_VERSION,
                callable_path="vfworks.actions.evaluate_model",
                retry_safe=True,
                request_type=EvaluateModelRequest,
                result_type=EvaluateModelResult,
            ),
        )
    )


def get_action_definition(
    name: str,
    *,
    version: str | None = None,
    registry: ActionRegistry | None = None,
) -> ActionDefinition:
    """Look up an action definition from the supplied or default registry."""

    selected_registry = registry or default_action_registry()
    return selected_registry.get(name, version=version)


def _type_path(value: type) -> str:
    return f"{value.__module__}.{value.__qualname__}"
