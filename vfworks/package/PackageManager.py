#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from pathlib import Path

import yaml


class PackageManager(object):
    def __init__(self, name='PackageManager', description='Built-in package manager', verbose=False):
        """Initialize a validity frame package manager."""

        self._name = name
        self._description = description
        self._verbose = verbose

        self._packageName = "vf_package"
        self.standalonePath = ""
        self._directory = Path.cwd()

    @property
    def name(self):
        """The name property (read-only)."""
        return self._name

    @property
    def description(self):
        """The description property (read-only)."""
        return self._description

    def create(self, name=None, force=False, standalone=False, path=None, config=None):
        """Create a validity frame package structure.

        Parameters
        ----------
        name : string
            Name of the validity frame package. When omitted, the current
            directory is used as the package root.
        force : bool
            Force creation in a non-empty current directory.
        standalone : bool
            Create the package in a child directory instead of the current directory.
        path : string
            Root path where the standalone package needs to be generated.
        config : dict
            Optional configuration to write to ``Resources/config.yaml``.
        """
        if standalone:
            root = Path(path) if path is not None else Path.cwd()
            package_name = name or self._packageName
            self.standalonePath = str(root)
            package_path = root / package_name
        else:
            package_path = Path(name) if name else Path.cwd()
            if package_path == Path.cwd() and not force and not self._checkEmptyDir():
                if self._verbose:
                    print("DEBUG: directory is not empty, no validity frame package created!")

        if self._verbose:
            print(f"DEBUG: creating validity frame package at {package_path}...")

        try:
            self._populatePackage(path=package_path, config=config)
        except Exception as exc:
            raise Exception("ERROR: validity frame package could not be created!") from exc

        if self._verbose:
            print("DEBUG: validity frame package created...")

        return package_path

    def check(self, path: str | Path = None) -> bool:
        """Check whether a path looks like a validity frame package."""
        package_path = Path(path) if path else Path.cwd()
        if self._verbose:
            print(f"DEBUG: checking validity frame package in {package_path}...")

        required_directories = [
            "Metadata",
            "Operational",
            "Processes",
            "Experiments",
            "Resources",
            "Sources",
            "Documentation",
            "Binaries",
        ]
        return (package_path / "validity_frame.ini").is_file() and all(
            (package_path / folder).is_dir() for folder in required_directories
        )

    def init_config(self, packageName=None):
        """Load an existing package config or return a default validity frame config."""
        package_path = self._normalize_package_path(packageName)
        existing_config = package_path / "Resources" / "config.yaml"
        if existing_config.exists():
            return self.load_config(existing_config)

        return self.default_config(package_path)

    def default_config(self, package_path=None):
        """Return the default validity frame configuration."""
        package_name = str(package_path or ".")
        return dict(
            validityframe={"name": package_name},
            logging={
                "level": "DEBUG",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "Resources/VF_BLDC.log",
            },
            dp_config={
                "storage_type": "global",
                "redis_host": "localhost",
                "redis_port": 6379,
                "redis_db": 0,
            },
        )

    def load_config(self, config_file):
        """Load a YAML config file."""
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)

    def _checkEmptyDir(self):
        """Function to determine if the current directory is empty."""
        if self._verbose:
            print("DEBUG: Checking if directory is empty...")
        return not any(self._directory.iterdir())

    def _populatePackage(self, path=None, config=None):
        """Function to populate the empty validity frame package."""
        package_path = self._normalize_package_path(path)
        self._packageName = package_path.name

        package_path.mkdir(parents=True, exist_ok=True)
        self._addFile(
            file="validity_frame.ini",
            name=self._packageName,
            description="Add project description",
            path=package_path,
        )

        for folder in [
            "Metadata",
            "Operational",
            "Processes",
            "Experiments",
            "Resources",
            "Sources",
            "Documentation",
            "Binaries",
        ]:
            self._mkdir_custom(package_path / folder, file="readme.rst")

        self._write_config(package_path, config or self.default_config(package_path))
        self._add_log_file(package_path, config)

    def _mkdir_custom(self, folder="empty", file='readme.rst'):
        """CUSTOM mkdir function to initialize git-pushable directories."""
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        self._addFile(file=file, path=folder)

    def _addFile(self, file="requirements.txt", name="", description="", tag="", path=None):
        """Function to add a file to the provided path."""
        target_dir = Path(path) if path is not None else self._directory
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / file

        if target.exists():
            return

        content = ""
        if "__init__.py" in file:
            content = ""
        elif "readme" in file:
            content = "Placeholder"
        elif "sys.log" in file or file.endswith(".log"):
            content = "---------------------- validity frame system logs ----------------------\n"
        elif "validity_frame.ini" in file:
            content = (
                "[ValidityFrame]\n"
                f"name = {name}\n"
                f'description = "{description or "Add project description"}"\n'
                "\n"
                "[PACKAGE]\n"
                f"name = {name}\n"
                "prefix =  \n"
            )
        elif "config.yaml" in file:
            content = yaml.safe_dump(self.default_config(target_dir.parent), sort_keys=False)

        target.write_text(content, encoding="utf-8")

    def _write_config(self, package_path, config):
        config_path = Path(package_path) / "Resources" / "config.yaml"
        if not config_path.exists():
            with open(config_path, "w") as f:
                yaml.safe_dump(config, f, sort_keys=False)

    def _add_log_file(self, package_path, config):
        if not config:
            config = self.default_config(package_path)
        log_file = config.get("logging", {}).get("file", None)
        if log_file:
            log_path = Path(package_path) / log_file
            log_path.parent.mkdir(parents=True, exist_ok=True)
            if not log_path.exists():
                self._addFile(file=log_path.name, path=log_path.parent)

    def _normalize_package_path(self, path=None):
        if not path:
            return Path(".")
        return path if isinstance(path, Path) else Path(path)
