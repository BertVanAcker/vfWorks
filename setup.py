#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# * 
# * This file is part of the vfWorks project.
# * 
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************

from setuptools import setup, find_packages

from vfworks import (
    __author__,
    __description__,
    __email__,
    __license__,
    __title__,
    __version__,
    __url__
)

#--- insert platform dependent setup ---
setup(
    name=__title__,
    version=__version__,
    description=__description__,
    long_description=open("README.md").read(),
    author=__author__,
    author_email=__email__,
    url=__url__,
    license=__license__,
    #install_requires=__install_requires__,
    python_requires=">=3.10",
    packages=find_packages(include=["vfworks", "vfworks.*"]),
    include_package_data=True,
    install_requires = [
        line.strip() for line in open('requirements.txt')],
    entry_points={
        "console_scripts": [
            "vfworks = rpio.__main__:main"
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