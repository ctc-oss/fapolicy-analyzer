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
from html.parser import HTMLParser
from os import path

import markdown2


def _parse_title_from_html(html):
    class H1Parser(HTMLParser):
        __parse_data = False
        headers = []

        def __is_h1(self, tag):
            return tag == "h1"

        def handle_starttag(self, tag, attrs):
            self.__parse_data = self.__is_h1(tag)

        def handle_endtag(self, tag):
            self.__parse_data = not self.__is_h1(tag)

        def handle_data(self, data):
            if self.__parse_data:
                self.headers.append(data)

    parser = H1Parser()
    parser.feed(html)
    return next(iter(parser.headers), None)


def _markdown_to_html(markdown_file, html_output_file):
    template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>{title}</title>
</head>
<body>
{body}
</body>
</html>
"""
    try:
        body = markdown2.markdown_path(markdown_file)
        title = _parse_title_from_html(body)
        html = template.format(title=title, body=body)
        with open(html_output_file, "w") as f:
            f.write(html)
    except Exception as e:
        print(e)
        return None

    return html_output_file


class parse_help(Command):
    description = "Update source controlled help documentation files from online source"
    user_options = [
        ("help-repo=", "r", "git repository of online help files"),
        ("help-commit", "c", "commit in help-repo to checkout, defaults to HEAD"),
        ("output-dir=", "o", "output directory"),
    ]
    help_files = ["User-Guide.md"]

    def initialize_options(self):
        self.help_repo = None
        self.help_commit = None
        self.output_dir = None

    def finalize_options(self):
        if not self.help_repo:
            self.help_repo = os.getenv(
                "HELP_REPO", "https://github.com/ctc-oss/fapolicy-analyzer.wiki.git"
            )
        if not self.help_commit:
            self.help_commit = os.getenv("HELP_COMMIT", "HEAD")
        if not self.output_dir:
            self.output_dir = "help"

    def run(self):
        c_files = self.build_help()
        self.update_pot(c_files)
        self.check_help(c_files)

    def __spawns(self, cmds):
        for cmd in cmds:
            self.spawn(cmd)

    def __clone_help_md(self):
        tmp_dir = path.join(self.output_dir, "tmp")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        clone_cmd = [
            "git",
            "clone",
            self.help_repo,
            "-b",
            "master",
            "--single-branch",
            tmp_dir,
        ]
        checkout_cmd = [
            "git",
            "-C",
            tmp_dir,
            "checkout",
            self.help_commit,
        ]
        self.__spawns([clone_cmd, checkout_cmd])
        shutil.rmtree(path.join(tmp_dir, ".git"), ignore_errors=True)
        return tmp_dir

    def build_help(self):
        # def filters():
        #     FILTERS = ["./scripts/pandoc_filters/local-links.lua"]
        #     return " ".join([f"--lua-filter='{f}'" for f in FILTERS])

        def html_file(file):
            rel_path = path.relpath(file, tmp_dir)
            return f"{path.join(c_dir, path.splitext(rel_path)[0])}.html"

        c_dir = path.join(self.output_dir, "C")
        os.makedirs(c_dir, exist_ok=True)
        tmp_dir = self.__clone_help_md()
        md_files = [path.join(tmp_dir, f) for f in self.help_files]
        html_files = [_markdown_to_html(md, html_file(md)) for md in md_files]
        shutil.rmtree(tmp_dir)
        return html_files

    def update_pot(self, c_files):
        pot_file = path.join(self.output_dir, "help.pot")
        itstool_cmd = ["itstool", "-o", pot_file, *c_files]
        self.spawn(itstool_cmd)

    def check_help(self, c_files):
        c_path = path.join(self.output_dir, "C")
        if not path.exists(c_path):
            return

        lint_cmds = [
            [
                "xmllint",
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
    description = "Build help documentation"
    user_options = [
        ("input-dir=", "i", "input directory of help files"),
        ("output-dir=", "o", "output directory of build"),
    ]

    def initialize_options(self):
        self.input_dir = None
        self.output_dir = None

    def finalize_options(self):
        self.input_dir = self.input_dir or "help"
        self.output_dir = self.output_dir or path.join("build", "help")

    def run(self):
        data_files = self.distribution.data_files or []
        data_files.extend(self.get_data_files())
        self.distribution.data_files = data_files
        self.check_help()

    def __spawns(self, cmds):
        for cmd in cmds:
            self.spawn(cmd)

    def get_data_files(self):
        def get_languages():
            lang_dirs = [
                d
                for d in os.listdir(self.input_dir)
                if path.isdir(path.join(self.input_dir, d)) and d != "tmp"
            ]
            return list(set(["C", *lang_dirs]))

        data_files = []
        name = self.distribution.metadata.name
        self.c_docs = glob(os.path.join(self.input_dir, "C", "*.docbook"))
        self.selected_languages = get_languages()

        for lang in self.selected_languages:
            source_path = path.join(self.input_dir, lang)
            build_path = path.join(self.output_dir, lang)
            os.makedirs(build_path, exist_ok=True)

            if lang != "C":
                po_file = path.join(source_path, lang + ".po")
                mo_file = path.join(build_path, lang + ".mo")

                msgfmt = ["msgfmt", po_file, "-o", mo_file]
                self.spawn(msgfmt)
                itstool_cmds = [
                    ["itstool", "-m", mo_file, "-o", build_path, page]
                    for page in self.c_docs
                ]
                self.__spawns(itstool_cmds)
            else:
                dir_util.copy_tree(source_path, build_path)

            docbook_files = glob("%s/*.docbook" % build_path)
            path_help = path.join("share", "help", lang, name)
            path_figures = path.join(path_help, "figures")
            data_files.append((path_help, docbook_files))
            figures = glob("%s/figures/*.png" % build_path)
            if figures:
                data_files.append((path_figures, figures))

        return data_files

    def check_help(self):
        for lang in self.selected_languages:
            build_path = path.join(self.output_dir, lang)
            if not path.exists(build_path):
                continue

            pages = [path.join(build_path, path.basename(p)) for p in self.c_docs]
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
