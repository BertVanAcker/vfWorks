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
    def __init__(self, name='PackageManager', description='Built-in package manager', verbose=False, packageName=None, packageLocation=None):
        """Initialize a validity frame package manager."""

        self._name = name
        self._description = description
        self._verbose = verbose

        self._packageName = packageName if packageName not in ("", ".") else None
        self.standalonePath = ""
        self._directory = Path.cwd() if packageLocation is None else Path(packageLocation)
        self._package_root = self._resolve_package_root(self._packageName)

    @property
    def name(self):
        """The name property (read-only)."""
        return self._name

    @property
    def description(self):
        """The description property (read-only)."""
        return self._description

    @property
    def packageName(self):
        """The packageName property (read-only)."""
        return self._packageName

    @property
    def directory(self):
        """The directory property (read-only)."""
        return self._directory

    @property
    def package_root(self):
        """The resolved root directory containing the VF package folders."""
        return self._package_root

    def create(self, name=None, force=False, standalone=False, config=None):
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
        package_name = name if name not in ("", ".") else None
        if standalone and package_name is not None:
            root = self._directory
            self.standalonePath = str(root)
            package_path = root / package_name
        else:
            package_path = self._directory if package_name is None else self._directory / package_name
            if package_path == self._directory and not force and not self._checkEmptyDir():
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

        self._package_root = package_path
        self._packageName = package_name
        return package_path

    def check(self, path: str | Path = None) -> bool:
        """Check whether a path looks like a validity frame package."""
        package_path = Path(path) if path else self._package_root
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
        package_path = self._resolve_package_root(packageName if packageName is not None else self._packageName)
        self._package_root = package_path
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
        return not self._directory.exists() or not any(self._directory.iterdir())

    def _populatePackage(self, path=None, config=None):
        """Function to populate the empty validity frame package."""
        package_path = self._normalize_package_path(path)
        self._package_root = package_path

        package_path.mkdir(parents=True, exist_ok=True)
        self._addFile(
            file="validity_frame.ini",
            name=self._packageName or package_path.name,
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

        for folder in ["loaders", "monitors"]:
            self._mkdir_custom(package_path/ "Resources" / folder, file="readme.rst")

        self._addFile(file="testType.py", path=package_path / "Resources" / "loaders")
        self._addFile(file="custom_monitor_example.py", path=package_path / "Resources" / "monitors")

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
        elif file == "testType.py":
            content = (
                '"""Template for Custom Model Loaders\n'
                "\n"
                "Filename should be renamed to match your specific model type (e.g., 'scikit_model.py')\n"
                "and invoked via loadModel(type='scikit_model')\n"
                '"""\n'
                "\n"
                "# Import your required third-party frameworks here\n"
                "# import joblib\n"
                "# import xgboost as xgb\n"
                "# import tensorrt as trt\n"
                "\n"
                "def load_model(model_location, validityframe=None):\n"
                '    """\n'
                "    Dynamically executed by ModelLoader when this framework type is requested.\n"
                "\n"
                "    Parameters:\n"
                "    -----------\n"
                "    model_location : str\n"
                "        The path to the model artifact (file or directory).\n"
                "    validityframe : object, optional\n"
                "        The active instance of the Validity Frame lifecycle manager.\n"
                "        Allows access to logging via `validityframe.logger.info()` or\n"
                "        global configurations via `validityframe.activeModelStructure`.\n"
                "\n"
                "    Returns:\n"
                "    --------\n"
                "    model : object\n"
                "        The initialized model object ready for predictions.\n"
                '    """\n'
                "    # 1. (Optional) Log the initiation of the custom process\n"
                "    if validityframe and hasattr(validityframe, 'logger'):\n"
                '        validityframe.logger.info(msg=f"Starting custom model loading from: {model_location}")\n'
                "\n"
                "    # =========================================================================\n"
                "    # FUNCTIONAL CODE TEMPLATE (Uncomment and customize for your framework)\n"
                "    # =========================================================================\n"
                "    # try:\n"
                "    #     # Example A: Loading a standard Scikit-Learn/Joblib pickle\n"
                "    #     loaded_model = joblib.load(model_location)\n"
                "    #     return loaded_model\n"
                "    #\n"
                "    #     # Example B: Loading a Deep Learning model weight package\n"
                "    #     # loaded_model = MyCustomNeuralNet()\n"
                "    #     # loaded_model.load_weights(model_location)\n"
                "    #     # return loaded_model\n"
                "    # except Exception as e:\n"
                "    #     if validityframe and hasattr(validityframe, 'logger'):\n"
                '    #         validityframe.logger.error(msg=f"Custom loader failed: {str(e)}")\n'
                "    #     raise e\n"
                "    # =========================================================================\n"
                "\n"
                "    # Default fallback if code isn't implemented yet\n"
                "    raise NotImplementedError(\n"
                '        "The load_model function must be implemented and return a model object."\n'
                "    )\n"
            )
        elif file == "custom_monitor_example.py":
            content = (
                '"""Template for Custom Monitor Validation\n'
                "\n"
                "Filename should be renamed to match your designated filename in the Validity Frame\n"
                "(e.g., 'custom_monitor_example.py') and is invoked automatically\n"
                "when Monitor.validate_point(...) runs for that monitor.\n"
                '"""\n'
                "\n"
                "# Import your required third-party frameworks here\n"
                "# import numpy as np\n"
                "# import pandas as pd\n"
                "\n"
                "\n"
                "def validate(monitor=None, **kwargs):\n"
                '    """\n'
                "    Dynamically executed by Monitor when this monitor has a matching custom script.\n"
                "\n"
                "    Parameters:\n"
                "    -----------\n"
                "    **kwargs : dict\n"
                "        Keyword context passed by Monitor.validate_point(...). Contains\n"
                "        data_vector, monitor, and each feature name as a direct keyword.\n"
                "    monitor : object, optional\n"
                "        The active Monitor instance. Allows access to monitor.name,\n"
                "        monitor.observes, monitor.spec_status, and monitor.last_observed_values.\n"
                "\n"
                "    Returns:\n"
                "    --------\n"
                "    evaluations : dict\n"
                "        Mapping of feature names to boolean validity statuses. Features omitted\n"
                "        from this dictionary fall back to their built-in specification checks.\n"
                '    """\n'
                "    # 1. Pull out the context you need. The rest of this function is yours to define.\n"
                '    data_vector = kwargs.get("data_vector", kwargs)\n'
                '    monitor = kwargs.get("monitor", monitor)\n'
                '    red = data_vector.get("colorRed", 0)\n'
                '    green = data_vector.get("colorGreen", 0)\n'
                '    blue = data_vector.get("colorBlue", 0)\n'
                "\n"
                "    # =========================================================================\n"
                "    # FUNCTIONAL CODE TEMPLATE (Customize for your monitor logic)\n"
                "    # =========================================================================\n"
                "    # Example: evaluate a cross-feature RGB envelope. This can express rules\n"
                "    # that individual per-feature specifications cannot capture by themselves.\n"
                "    # is_valid_red = 200 <= red <= 255\n"
                "    # is_valid_green = 200 <= green <= 255\n"
                "    # is_valid_blue = 200 <= blue <= 255\n"
                "    #\n"
                "    # return {\n"
                '    #     "colorRed": is_valid_red,\n'
                '    #     "colorGreen": is_valid_green,\n'
                '    #     "colorBlue": is_valid_blue,\n'
                "    # }\n"
                "    # =========================================================================\n"
                "\n"
                "    # Default fallback if code isn't implemented yet\n"
                "    raise NotImplementedError(\n"
                '        "The validate function must return a feature-to-bool mapping."\n'
                "    )\n"
            )

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
            return self._package_root
        return path if isinstance(path, Path) else Path(path)

    def _resolve_package_root(self, packageName=None):
        if packageName in (None, "", "."):
            return self._directory
        package_path = packageName if isinstance(packageName, Path) else Path(packageName)
        if package_path.is_absolute():
            return package_path
        return self._directory / package_path
