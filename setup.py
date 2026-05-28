#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# * 
# * This file is part of the vfWorks project.
# * 
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************

from pathlib import Path

import tomllib

from setuptools import find_packages, setup

pyproject_path = Path(__file__).with_name("pyproject.toml")
project_metadata = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))["project"]
project_author = ", ".join(author["name"] for author in project_metadata.get("authors", []))
project_email = ", ".join(author["email"] for author in project_metadata.get("authors", []) if author.get("email"))
project_license = project_metadata.get("license", {}).get("text", "")
project_url = project_metadata.get("urls", {}).get("Homepage", "")

#--- insert platform dependent setup ---
setup(
    name=project_metadata["name"],
    version=project_metadata["version"],
    description=project_metadata["description"],
    long_description=Path("README.md").read_text(encoding="utf-8"),
    author=project_author,
    author_email=project_email,
    url=project_url,
    license=project_license,
    python_requires=">=3.12",
    packages=find_packages(include=["vfworks", "vfworks.*"]),
    include_package_data=True,
    install_requires=project_metadata["dependencies"],
    entry_points={
        "console_scripts": [
            "vfworks = vfworks.__main__:cli"
        ]
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    keywords=[
        "AI",
        "Safety",
        "Model-based",
    ],
)