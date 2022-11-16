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
import urllib.request
from distutils.cmd import Command
from logging import getLogger
from os import path
from typing import Sequence
from urllib.parse import urlparse

import markdown2
from bs4 import BeautifulSoup

logger = getLogger(__name__)


def _parse_media_urls(html: str, filter: str) -> Sequence[str]:
    soup = BeautifulSoup(html, "html.parser")
    return [
        url
        for url in [img.get("src") for img in soup("img")]
        if url and url.startswith(filter)
    ]


def _markdown_to_html(markdown_file: str) -> str:
    def get_title():
        soup = BeautifulSoup(body, "html.parser")
        header = soup.find("h1")
        return header.get_text() if header else "User Guide"

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
    body = markdown2.markdown_path(markdown_file, extras=["header-ids"])
    title = get_title()
    return template.format(title=title, body=body)


class build_help(Command):
    description = "Update source controlled help documentation files from online source"
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
        self.output_dir = None
        self.proxy = None

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
        c_files = self.__parse_help()
        self.__check_help(c_files)
        self.__generate_translation_template(c_files)

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

    def __download_file(self, url, filename):
        try:
            if self.proxy:
                proxy_handler = urllib.request.ProxyHandler(
                    {urlparse(url).scheme: self.proxy}
                )
                opener = urllib.request.build_opener(proxy_handler)
            else:
                opener = urllib.request.build_opener()

            os.makedirs(path.dirname(filename), exist_ok=True)
            with opener.open(url) as response, open(filename, "wb") as out_file:
                out_file.write(response.read())
        except Exception as e:
            logger.error(f"Unable to download file from {url}", e)

    def __parse_help(self):
        def html_file(md, html):
            rel_path = path.relpath(md, tmp_dir)
            full_path = f"{path.join(c_dir, path.splitext(rel_path)[0])}.html"
            with open(full_path, "w") as file:
                file.write(html)
            return full_path

        c_dir = path.join(self.output_dir, "C")
        os.makedirs(c_dir, exist_ok=True)
        tmp_dir = self.__clone_help_md()
        md_files = [path.join(tmp_dir, f) for f in self.help_files]
        html_files = []
        for md in md_files:
            html = _markdown_to_html(md)
            media_urls = _parse_media_urls(
                html, "https://user-images.githubusercontent.com/1545372"
            )
            for url in media_urls:
                filename = path.basename(urlparse(url).path)
                local_path = path.join("media", filename)
                self.__download_file(url, path.join(c_dir, local_path))
                rel_path = f"help:fapolicy-analyzer/{local_path}"
                html = html.replace(url, rel_path)
            html_files.append(html_file(md, html))
        shutil.rmtree(tmp_dir)
        return html_files

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
