# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

from setuptools import find_namespace_packages, setup
from setuptools_rust import RustExtension


def get_version():
    if "VERSION" in os.environ:
        return os.getenv("VERSION")
    if os.path.exists("VERSION"):
        with open("VERSION", "r") as version:
            v = version.readline().strip()
            if len(v):
                return v
    try:
        from version import get_versions
    except Exception:
        raise RuntimeError("Unable to import git describe version generator")
    meta = get_versions()
    if "version" not in meta:
        raise RuntimeError("Could not parse version from Git")
    return meta["version"]


# comma separated list of features that should be enabled in the rust build
def get_features():
    enabling = None
    if "FEATURES" in os.environ:
        enabling = os.getenv("FEATURES")
    if os.path.exists("FEATURES"):
        with open("FEATURES", "r") as features:
            v = features.readline().strip().split(",")
            if len(v):
                enabling = v
    print(f"Enabled Rust features: {enabling}")
    return enabling

#
# rm -rf fapolicy_analyzer.egg-info/ build/ dist/ && python setup.py bdist_wheel
#
setup(
    name="fapolicy-analyzer",
    version=get_version(),
    packages=find_namespace_packages(
        include=[
            "fapolicy_analyzer",
            "fapolicy_analyzer.css",
            "fapolicy_analyzer.glade",
            "fapolicy_analayzer.locale*",
            "fapolicy_analyzer.redux*",
            "fapolicy_analyzer.resources*",
            "fapolicy_analyzer.ui*",
            "fapolicy_analyzer.util",
        ],
    ),
    setup_requires=["setuptools", "setuptools_rust"],
    zip_safe=False,
    rust_extensions=[
        RustExtension("fapolicy_analyzer.rust", path="crates/pyo3/Cargo.toml", features=get_features())
    ],
    include_package_data=True,
    package_data={
        "fapolicy_analyzer.css": ["*.css"],
        "fapolicy_analyzer.glade": ["*.glade"],
        "fapolicy_analyzer.resources": ["*"],
        "fapolicy_analyzer.resources.sourceview.language-specs": ["*.lang"],
        "fapolicy_analyzer.resources.sourceview.styles": ["*.xml"],
    },
)
