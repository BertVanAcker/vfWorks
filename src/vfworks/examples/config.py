from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TaskConfig:
    name: str
    method: str


@dataclass(frozen=True)
class ExampleConfig:
    source: Path
    name: str
    root: Path
    working_directory: Path
    validity_frame: dict[str, Any]
    active_model_structure: str | None
    actions_file: Path
    actions_class: str
    actions_arguments: dict[str, Any]
    tasks: tuple[TaskConfig, ...]
    active_model_structure_name: str | None = None


def _path(base: Path, value: str, field: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{field}' must be a non-empty path")
    candidate = Path(value)
    return (base / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()


def load_example_config(path: str | Path) -> ExampleConfig:
    """Load a vfWorks example without importing or executing example code."""
    try:
        import yaml
    except ImportError as error:
        raise RuntimeError("PyYAML is required to load an example configuration") from error

    source = Path(path).resolve()
    with source.open(encoding="utf-8") as stream:
        raw = yaml.safe_load(stream)
    if not isinstance(raw, dict):
        raise ValueError("Example configuration must be a mapping")

    base = source.parent
    root = _path(base, raw.get("root", "."), "root")
    actions = raw.get("actions", {})
    validity_frame = raw.get("validity_frame", {})
    task_values = raw.get("tasks", [])
    if not isinstance(actions, dict) or not isinstance(validity_frame, dict):
        raise ValueError("'actions' and 'validity_frame' must be mappings")
    if not isinstance(task_values, list) or not task_values:
        raise ValueError("'tasks' must be a non-empty list")

    tasks = tuple(TaskConfig(name=item["name"], method=item["method"]) for item in task_values)
    if len({task.name for task in tasks}) != len(tasks):
        raise ValueError("Task names must be unique")

    return ExampleConfig(
        source=source,
        name=raw.get("name", source.stem),
        root=root,
        working_directory=_path(root, raw.get("working_directory", "Processes"), "working_directory"),
        validity_frame=dict(validity_frame),
        active_model_structure=raw.get("active_model_structure"),
        actions_file=_path(root, actions.get("file", "Processes/Actions/trainer.py"), "actions.file"),
        actions_class=actions.get("class", "trainingActions"),
        actions_arguments=dict(actions.get("arguments", {})),
        tasks=tasks,
        active_model_structure_name=raw.get("active_model_structure_name"),
    )
