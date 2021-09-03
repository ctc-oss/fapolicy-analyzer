import os
from setuptools import setup, find_namespace_packages
from setuptools_rust import RustExtension


#
# rm -rf fapolicy_analyzer.egg-info/ build/ dist/ && python setup.py bdist_wheel
#
setup(
    name="fapolicy-analyzer",
    version=os.getenv("VERSION", "snapshot"),
    packages=find_namespace_packages(
        include=["fapolicy_analyzer", "fapolicy_analyzer.*"], exclude=["*.tests"]
    ),
    setup_requires=["setuptools", "setuptools_rust"],
    zip_safe=False,
    rust_extensions=[RustExtension("fapolicy_analyzer.rust", path="crates/pyo3/Cargo.toml")],
    include_package_data=True,
    package_data={
        "fapolicy_analyzer": ["locale/*/LC_MESSAGES/*.mo"],
        "fapolicy_analyzer.css": ["*.css"],
        "fapolicy_analyzer.glade": ["*.glade"],
        "fapolicy_analyzer.resources": ["*"],
    },
)
