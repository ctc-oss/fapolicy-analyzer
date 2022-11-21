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
from distutils.cmd import Command
from glob import glob
from logging import getLogger
from os import path

logger = getLogger(__name__)


class build_help(Command):
    description = "Update source controlled help documentation files from online source"
    user_options = [
        (
            "force-refresh=",
            "f",
            "force download even if help files are available locally",
        ),
        ("help-repo=", "r", "git repository of online help files"),
        ("help-commit=", "c", "commit in help-repo to checkout, defaults to HEAD"),
        ("output-dir=", "o", "output directory"),
        ("proxy=", "p", "proxy server for file downloads"),
    ]
    help_files = ["User-Guide.md"]

    def initialize_options(self):
        self.help_repo = None
        self.help_commit = None
        self.output_dir = None
        self.proxy = None
        self.force_refresh = False

    def finalize_options(self):
        if not self.help_repo:
            self.help_repo = os.getenv(
                "HELP_REPO", "https://github.com/ctc-oss/fapolicy-analyzer.wiki.git"
            )
        if not self.help_commit:
            self.help_commit = os.getenv("HELP_COMMIT", "HEAD")
            logger.info(f"HELP_COMMIT={self.help_commit}")
        if not self.output_dir:
            self.output_dir = "help"

    def run(self):
        c_files = self.__parse_help()
        self.__check_help(c_files)
        self.__generate_translation_template(c_files)

    def __spawns(self, cmds):
        for cmd in cmds:
            self.spawn(cmd)

    def __parse_help(self):
        c_dir = path.join(self.output_dir, "C")

        if os.path.isdir(c_dir) and len(os.listdir(c_dir)) and not self.force_refresh:
            _glob = rf"{c_dir}/**/*.html"
            return glob(_glob, recursive=True)

        if self.force_refresh:
            shutil.rmtree(c_dir)

        import help

        return help.download(
            self.help_files,
            self.help_repo,
            self.help_commit,
            self.output_dir,
            proxy=self.proxy,
        )

    def __generate_translation_template(self, c_files):
        pot_file = path.join(self.output_dir, "help.pot")
        itstool_cmd = ["itstool", "-o", pot_file, *c_files]
        self.spawn(itstool_cmd)

    def __check_help(self, c_files):
        c_path = path.join(self.output_dir, "C")
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
