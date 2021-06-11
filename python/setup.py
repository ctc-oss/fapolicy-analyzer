import os
from setuptools import setup, find_packages
from setuptools_rust import RustExtension

#
# rm -rf fapolicy_analyzer.egg-info/ build/ dist/ && python setup.py bdist_wheel
#
setup(
    name="fapolicy-analyzer",
    version=os.getenv("VERSION", "snapshot"),
    packages=["glade", "resources"] + find_packages(exclude=("tests",)),
    setup_requires=["setuptools", "setuptools_rust"],
    zip_safe=False,
    rust_extensions=[RustExtension("fapolicy_analyzer.rust")],
    include_package_data=True,
    package_data={
        "glade": ["*.glade"],
        "resources": ["*"]
    }
)
