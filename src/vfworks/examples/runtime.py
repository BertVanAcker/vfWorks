from __future__ import annotations

import importlib.util
import os
import sys
from collections import OrderedDict
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Callable, Iterator

from .config import ExampleConfig


@contextmanager
def _example_context(directory: Path) -> Iterator[None]:
    """Provide the relative-path/import context expected by legacy examples."""
    previous = Path.cwd()
    entry = str(directory)
    sys.path.insert(0, entry)
    os.chdir(directory)
    try:
        yield
    finally:
        os.chdir(previous)
        if sys.path and sys.path[0] == entry:
            sys.path.pop(0)


def _load_module(path: Path) -> ModuleType:
    module_name = f"vfworks_example_{abs(hash(path))}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load example actions from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExampleRuntime:
    """Instantiate and expose an example described entirely by configuration."""

    def __init__(self, config: ExampleConfig):
        self.config = config
        self.validity_frame = None
        self.actions = None

    def load(self) -> "ExampleRuntime":
        from vfworks.metamodels.validity_frame import ValidityFrame

        with _example_context(self.config.working_directory):
            vf_arguments = dict(self.config.validity_frame)
            for key in ("config", "VFPackage"):
                value = vf_arguments.get(key)
                if isinstance(value, str) and not Path(value).is_absolute():
                    vf_arguments[key] = str((self.config.root / value).resolve())
            self.validity_frame = ValidityFrame(**vf_arguments)
            if self.config.active_model_structure:
                self.validity_frame.setActiveModelStructure(GUID=self.config.active_model_structure)
            elif self.config.active_model_structure_name:
                self.validity_frame.setActiveModelStructure(name=self.config.active_model_structure_name)

            module = _load_module(self.config.actions_file)
            actions_type = getattr(module, self.config.actions_class)
            arguments = dict(self.config.actions_arguments)
            arguments.setdefault("validityFrame", self.validity_frame)
            self.actions = actions_type(**arguments)
        return self

    def tasks(self) -> OrderedDict[str, Callable[[], object]]:
        if self.actions is None:
            self.load()
        return OrderedDict(
            (task.name, getattr(self.actions, task.method)) for task in self.config.tasks
        )

    def execution_context(self):
        """Return the path/import context required by this example's actions."""
        return _example_context(self.config.working_directory)

    def run_headless(self) -> bool:
        """Run configured actions synchronously and stop at the first failure."""
        with _example_context(self.config.working_directory):
            for name, action in self.tasks().items():
                result = action()
                if result is False:
                    raise RuntimeError(f"Task '{name}' reported failure")
        return True
