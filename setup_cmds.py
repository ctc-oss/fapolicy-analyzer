# Copyright Concurrent Technologies Corporation 2022
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
import shutil
from distutils import dir_util
from distutils.cmd import Command
from glob import glob
from logging import getLogger
from os import path

logger = getLogger(__name__)


class update_help(Command):
    description = "Update help documentation files from online source"
    user_options = [
        ("help-repo=", "r", "git repository of online help files"),
        ("help-commit=", "c", "commit in help-repo to checkout, defaults to HEAD"),
        ("output-dir=", "o", "output directory"),
        ("proxy=", "p", "proxy server for file downloads"),
    ]
    help_files = ["User-Guide.md"]

    def initialize_options(self):
        self.help_repo = None
        self.help_commit = None
        self.build_dir = None
        self.proxy = None

    def finalize_options(self):
        if not self.help_repo:
            self.help_repo = os.getenv(
                "HELP_REPO", "https://github.com/ctc-oss/fapolicy-analyzer.wiki.git"
            )
        if not self.help_commit:
            self.help_commit = os.getenv("HELP_COMMIT", "HEAD")
            logger.info(f"HELP_COMMIT={self.help_commit}")
        if not self.build_dir:
            self.build_dir = "help"

    def run(self):
        c_files = self.__parse_help()
        self.__check_help(c_files)
        self.__generate_translation_template(c_files)

    def __spawns(self, cmds):
        for cmd in cmds:
            self.spawn(cmd)

    def __parse_help(self):
        c_dir = path.join(self.build_dir, "C")
        shutil.rmtree(c_dir, ignore_errors=True)

        import setup_help_utils

        return setup_help_utils.download(
            self.help_files,
            self.help_repo,
            self.help_commit,
            self.build_dir,
            proxy=self.proxy,
        )

    def __generate_translation_template(self, c_files):
        pot_file = path.join(self.build_dir, "help.pot")
        itstool_cmd = ["itstool", "-o", pot_file, *c_files]
        self.spawn(itstool_cmd)

    def __check_help(self, c_files):
        c_path = path.join(self.build_dir, "C")
        if not path.exists(c_path):
            return

        lint_cmds = [
            [
                "xmllint",
                "--html",
                "--noout",
                "--noent",
                "--path",
                c_path,
                "--xinclude",
                f,
            ]
            for f in c_files
            if path.exists(f)
        ]
        self.__spawns(lint_cmds)


class build_help(Command):
    description = "Build output directory of help files"
    user_options = [
        ("source=", "s", "Source directory of help files"),
        ("build=", "b", "Output directory of build"),
    ]

    def initialize_options(self):
        self.source_dir = None
        self.build_dir = None

    def finalize_options(self):
        self.source_dir = self.source_dir or "help"
        self.build_dir = self.build_dir or path.join("build", "help")

    def run(self):
        self.c_docs = glob(os.path.join(self.source_dir, "C", "*.html"))
        name = self.distribution.metadata.name
        self.selected_languages = self.__get_languages()

        for lang in self.selected_languages:
            source_path = path.join(self.source_dir, lang)
            build_path = path.join(self.build_dir, lang, name)
            os.makedirs(build_path, exist_ok=True)

            if lang != "C":
                po_file = path.join(source_path, lang + ".po")
                mo_file = path.join(build_path, lang + ".mo")

                # generate translated files
                msgfmt = ["msgfmt", po_file, "-o", mo_file]
                self.spawn(msgfmt)
                itstool_cmds = [
                    ["itstool", "-m", mo_file, "-o", build_path, page]
                    for page in self.c_docs
                ]
                self.__spawns(itstool_cmds)
                os.remove(mo_file)

                # copy media to language directory
                source_media = path.join(self.source_dir, "C", "media")
                build_media = path.join(build_path, "media")
                dir_util.copy_tree(source_media, build_media)
            else:
                dir_util.copy_tree(source_path, build_path)

    def __spawns(self, cmds):
        for cmd in cmds:
            self.spawn(cmd)

    def __get_languages(self):
        lang_dirs = [
            d
            for d in os.listdir(self.source_dir)
            if path.isdir(path.join(self.source_dir, d)) and d != "tmp"
        ]
        return list(set(["C", *lang_dirs]))
