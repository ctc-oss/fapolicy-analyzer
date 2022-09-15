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
from distutils.cmd import Command
from distutils.errors import DistutilsExecError
from glob import glob
from os import path

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


# def has_help(self):
#     return "build_help" in self.distribution.cmdclass


# build.sub_commands.extend(
#     [
#         ("build_help", has_help),
#     ]
# )


class build_help(Command):
    description = "Build Help Documentation"
    user_options = []
    help_dir = "help"
    build_dir = path.join("build", help_dir)

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        data_files = self.distribution.data_files or []
        data_files.extend(self.get_data_files())
        self.distribution.data_files = data_files
        self.check_help()

    def __spawns(self, cmds):
        for cmd in cmds:
            self.spawn(cmd)

    def get_data_files(self):
        def parse_ducktype_files(output):
            duck_files = path.join(self.help_dir, "src", "*.duck")
            try:
                os.makedirs(output, exist_ok=True)
                ducktype_cmd = ["ducktype", "-o", output, duck_files]
                self.spawn(["sh", "-c", " ".join(ducktype_cmd)])
                return glob(path.join(output, "*.page"))
            except DistutilsExecError as ex:
                print("Failed to parse Ducktype help files: {}".format(ex))
            return []

        def get_languages():
            lang_dirs = [
                d
                for d in os.listdir(self.help_dir)
                if path.isdir(path.join(self.help_dir, d)) and d != "src"
            ]
            return list(set(["C", *lang_dirs]))

        data_files = []
        name = self.distribution.metadata.name
        c_path = path.join(self.build_dir, "C")

        self.selected_languages = get_languages()
        self.C_PAGES = parse_ducktype_files(c_path)

        for lang in self.selected_languages:
            source_path = path.join(self.help_dir, lang)
            build_path = path.join(self.build_dir, lang)
            os.makedirs(build_path, exist_ok=True)

            if lang != "C":
                po_file = path.join(source_path, lang + ".po")
                mo_file = path.join(build_path, lang + ".mo")

                msgfmt = ["msgfmt", po_file, "-o", mo_file]
                self.spawn(msgfmt)
                itstool_cmds = [
                    ["itstool", "-m", mo_file, "-o", build_path, page]
                    for page in self.C_PAGES
                ]
                self.__spawns(itstool_cmds)

            mallard_files = glob("%s/*.page" % build_path)
            path_help = path.join("share", "help", lang, name)
            path_figures = path.join(path_help, "figures")
            data_files.append((path_help, mallard_files))
            figures = glob("%s/figures/*.png" % build_path)
            if figures:
                data_files.append((path_figures, figures))

        return data_files

    def check_help(self):
        for lang in self.selected_languages:
            build_path = path.join(self.build_dir, lang)
            if not path.exists(build_path):
                continue

            pages = [path.join(build_path, path.basename(p)) for p in self.C_PAGES]
            lint_cmds = [
                [
                    "xmllint",
                    "--noout",
                    "--noent",
                    "--path",
                    build_path,
                    "--xinclude",
                    page,
                ]
                for page in pages
                if path.exists(page)
            ]
            self.__spawns(lint_cmds)


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
        RustExtension("fapolicy_analyzer.rust", path="crates/pyo3/Cargo.toml")
    ],
    include_package_data=True,
    package_data={
        "fapolicy_analyzer": ["locale/*/LC_MESSAGES/*.mo"],
        "fapolicy_analyzer.css": ["*.css"],
        "fapolicy_analyzer.glade": ["*.glade"],
        "fapolicy_analyzer.resources": ["*"],
        "fapolicy_analyzer.resources.sourceview.language-specs": ["*.lang"],
        "fapolicy_analyzer.resources.sourceview.styles": ["*.xml"],
    },
    cmdclass={"build_help": build_help},
)
