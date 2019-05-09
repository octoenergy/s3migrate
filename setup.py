#!/usr/bin/env python
# -*- coding: utf-8 -*
import pathlib
from setuptools import find_packages, setup

VERSION = "0.0.1-alpha.1"

REPO_ROOT = pathlib.Path(__file__).parent

with open(REPO_ROOT / "README.md", encoding="utf-8") as f:
    README = f.read()

REQUIREMENTS = [
    # S3 access
    "s3fs",
]


setup_args = dict(
    # Description
    name="s3migrate",
    version=VERSION,
    description="Change key structure with ease - make your data Athena-ready",
    long_description=README,
    long_description_content_type='text/markdown',
    # Credentials
    author="Octopus Energy",
    author_email="nerds@octoenergy.com",
    url="https://github.com/octoenergy/s3migrate",
    license="MIT",
    # Package data
    package_dir={"": "src"},
    packages=find_packages("src", include=["*s3migrate*"]),
    entry_points={"console_scripts": []},
    include_package_data=False,
    # Dependencies
    install_requires=REQUIREMENTS,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Typing :: Typed",
    ],
)


if __name__ == "__main__":

    # Make install
    setup(**setup_args)
