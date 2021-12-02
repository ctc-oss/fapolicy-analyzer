"""Setup script for redux-py"""

from os.path import abspath, dirname, join
from pathlib import Path
from typing import Sequence

from setuptools import find_packages, setup

# The directory containing this file
HERE = abspath(dirname(__file__))

# The text of the README file
with open(join(HERE, "README.md")) as fid:
    README = fid.read()


def read(fname: str) -> str:
    return open(Path(__file__).parent / fname).read()


def read_requirements(filename: str) -> Sequence[str]:
    return read(filename).splitlines()


# This call to setup() does all the work
setup(
    name="redux-py",
    version="0.1.12",
    description="Redux implementation for Python",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Carsten-Leue/ReduxPY",
    author="Dr. Carsten Leue",
    author_email="carsten.leue@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3",
        'Typing :: Typed'
    ],
    install_requires=read_requirements('requirements.txt'),
    tests_require=read_requirements('test-requirements.txt'),
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    zip_safe=False
)
