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


import argparse
import os
import shutil
import subprocess
import urllib.request
from distutils import dir_util
from glob import glob
from os import makedirs, path, environ
from typing import Optional, Sequence
from urllib.parse import urlparse


DEFAULT_HELP_FILES = ["User-Guide.md"]
DEFAULT_REPO = "https://github.com/ctc-oss/fapolicy-analyzer.wiki.git"
DEFAULT_OUTPUT_DIR = "help"
DEFAULT_INSTALL_DIR = "share"
DEFAULT_MEDIA_URL = "https://user-images.githubusercontent.com/1545372"
DEFAULT_REL_MEDIA_DIR = "media"
DEFAULT_BUILD_DIR = path.join("build", DEFAULT_OUTPUT_DIR)

if environ.get("LOCAL_HELP_GFX"):
    DEFAULT_REL_HELP_GFX_PREFIX = ""
else:
    DEFAULT_REL_HELP_GFX_PREFIX = "help:fapolicy-analyzer/"

try:
    # attempt to read version from a file in the help dir
    with open("help/version") as f:
        DEFAULT_COMMIT = f.readline().strip() or "HEAD"
        print(f"Generating help content from git repo: {DEFAULT_COMMIT}")
except FileNotFoundError:
    DEFAULT_COMMIT = "HEAD"

def _runs(cmds):
    for cmd in cmds:
        subprocess.run(cmd, check=True)

def _clone_help(repo: str, commit: str, output_dir: str) -> str:
    tmp_dir = path.join(output_dir, "tmp")
    shutil.rmtree(tmp_dir, ignore_errors=True)
    clone_cmd = [
        "git",
        "clone",
        repo,
        "-b",
        "master",
        tmp_dir,
    ]
    checkout_cmd = [
        "git",
        "-C",
        tmp_dir,
        "checkout",
        commit,
    ]
    subprocess.run(clone_cmd, check=True)
    print(f"Checking out commit {commit}")
    subprocess.run(checkout_cmd, check=True)
    shutil.rmtree(path.join(tmp_dir, ".git"), ignore_errors=True)
    return tmp_dir

def _parse_media_urls(html: str, filter: str) -> Sequence[str]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    return [
        url
        for url in [img.get("src") for img in soup("img")]
        #if url and url.startswith(filter)
    ]

def _markdown_to_html(markdown_file: str) -> str:
    import markdown2
    from bs4 import BeautifulSoup

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

def _download_file(url: str, filename: str, proxy: Optional[str] = None):
    try:
        if proxy:
            proxy_handler = urllib.request.ProxyHandler({urlparse(url).scheme: proxy})
            opener = urllib.request.build_opener(proxy_handler)
        else:
            opener = urllib.request.build_opener()

        makedirs(path.dirname(filename), exist_ok=True)
        with opener.open(url) as response, open(filename, "wb") as out_file:
            out_file.write(response.read())
    except Exception as e:
        print(f"Unable to download file from {url}: {e}")

def _copy_from_local_clone(local_repo_path: str, filename: str):
    makedirs(path.dirname(filename), exist_ok=True)
    shutil.copyfile(local_repo_path, filename)


def _download(
    files: Sequence[str] = DEFAULT_HELP_FILES,
    repo: str = DEFAULT_REPO,
    commit: str = DEFAULT_COMMIT,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    media_url: str = DEFAULT_MEDIA_URL,
    proxy: Optional[str] = None,
) -> Sequence[str]:
    """
    Will download the latest help markdown files from the online help
    repository, convert the files to HTML, parse the HTML for media
    files, download the media files, and update the refs in the HTML.
    """

    def html_file(md, html):
        rel_path = path.relpath(md, tmp_dir)
        full_path = f"{path.join(c_dir, path.splitext(rel_path)[0])}.html"
        with open(full_path, "w") as file:
            file.write(html)
        return full_path

    tmp_dir = _clone_help(repo, commit, output_dir)
    c_dir = path.join(output_dir, "C")
    makedirs(c_dir, exist_ok=True)
    md_files = [path.join(tmp_dir, f) for f in files]
    html_files = []

    for md in md_files:
        html = _markdown_to_html(md)

        # Also include relative media
        media_urls = _parse_media_urls(html, media_url)
        for url in media_urls:

            # Construct path to relative media in fapolicy-analyzer.m
            url_tuple = urlparse(url)
            filename = path.basename(url_tuple.path)
            local_path = path.join(DEFAULT_REL_MEDIA_DIR, filename)
            rel_path = f"{DEFAULT_REL_HELP_GFX_PREFIX}{local_path}"

            # Copy from public wiki repo or from local wiki repo clone
            if url_tuple.scheme:
                _download_file(url, path.join(c_dir, local_path), proxy)
            else:
                _copy_from_local_clone(path.join(tmp_dir, url),
                                       path.join(c_dir, local_path))
                
            html = html.replace(url, rel_path)
        html_files.append(html_file(md, html))

    shutil.rmtree(tmp_dir)
    return html_files

def update_help(
    repo: str = DEFAULT_REPO,
    commit: str = DEFAULT_COMMIT,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    files: Sequence[str] = DEFAULT_HELP_FILES,
    proxy: Optional[str] = None,
):
    def _parse_help():
        c_dir = path.join(output_dir, "C")
        shutil.rmtree(c_dir, ignore_errors=True)

        return _download(
            files,
            repo,
            commit,
            output_dir,
            proxy=proxy,
        )

    def _generate_translation_template(c_files):
        pot_file = path.join(output_dir, "help.pot")
        itstool_cmd = ["itstool", "-o", pot_file, *c_files]
        subprocess.run(itstool_cmd, check=True)

    def _check_help(c_files):
        c_path = path.join(output_dir, "C")
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
        _runs(lint_cmds)

    c_files = _parse_help()
    _check_help(c_files)
    _generate_translation_template(c_files)


def _get_languages(source: str):
    lang_dirs = [
        d
        for d in os.listdir(source) if not d.startswith("_")
        if path.isdir(path.join(source, d)) and d != "tmp"
    ]
    return list({"C", *lang_dirs})


def build_help(
    source: str = DEFAULT_OUTPUT_DIR,
    build: str = DEFAULT_BUILD_DIR,
):
    c_docs = glob(path.join(source, "C", "*.html"))
    name = "fapolicy-analyzer"
    selected_languages = _get_languages(source)

    for lang in selected_languages:
        source_path = path.join(source, lang)
        build_path = path.join(build, lang, name)
        os.makedirs(build_path, exist_ok=True)

        if lang != "C":
            po_file = path.join(source_path, lang + ".po")
            mo_file = path.join(build_path, lang + ".mo")

            # generate translated files
            msgfmt = ["msgfmt", po_file, "-o", mo_file]
            subprocess.run(msgfmt, check=True)
            itstool_cmds = [
                ["itstool", "-m", mo_file, "-o", build_path, page] for page in c_docs
            ]
            _runs(itstool_cmds)
            os.remove(mo_file)

            # copy media to language directory
            source_media = path.join(source, "C", "media")
            build_media = path.join(build_path, "media")
            dir_util.copy_tree(source_media, build_media)
        else:
            dir_util.copy_tree(source_path, build_path)


def install_help(
        source: str = DEFAULT_BUILD_DIR,
        dest: str = DEFAULT_INSTALL_DIR,
):
    name = "fapolicy-analyzer"
    print(f"Installing langs to {dest}")
    selected_languages = _get_languages(source)
    for lang in selected_languages:
        print(f"\t{lang}")
        lang_source = path.join(source, lang)
        lang_dest = path.join(dest, lang, name)
        dir_util.copy_tree(lang_source, lang_dest)


def _args():
    parser = argparse.ArgumentParser(
        description="Utility scripts for working with help documentation files"
    )
    subpar = parser.add_subparsers(title="Commands", help="Command help")

    parser_up = subpar.add_parser(
        "update", help="Update the local help documentation files"
    )
    parser_up.set_defaults(cmd=update_help)
    parser_up.add_argument(
        "-r", "--repo", help="Git repo to download from", default=DEFAULT_REPO
    )
    parser_up.add_argument(
        "-c", "--commit", help="Git commit to download", default=DEFAULT_COMMIT
    )
    parser_up.add_argument(
        "-o", "--output_dir", help="Directory to output to", default=DEFAULT_OUTPUT_DIR
    )
    parser_up.add_argument(
        "-f",
        "--files",
        nargs="*",
        help="List of help files to download separated by spaces",
        default=DEFAULT_HELP_FILES,
    )
    parser_up.add_argument("-p", "--proxy", help="HTTPS proxy to use for downloading")

    parser_b = subpar.add_parser(
        "build", help="Build help documentation for distribution"
    )
    parser_b.set_defaults(cmd=build_help)
    parser_b.add_argument(
        "-s",
        "--source",
        help="Source directory of the help documentation",
        default=DEFAULT_OUTPUT_DIR,
    )
    parser_b.add_argument(
        "-b",
        "--build",
        help="Directory to output the build to",
        default=DEFAULT_BUILD_DIR,
    )

    parser_i = subpar.add_parser(
        "install", help="Install help documentation"
    )
    parser_i.set_defaults(cmd=install_help)
    parser_i.add_argument(
        "--source",
        help="The built documentation to install",
        default=DEFAULT_OUTPUT_DIR,
    )
    parser_i.add_argument(
        "-d",
        "--dest",
        help="Target installation directory",
        default=DEFAULT_INSTALL_DIR
    )

    return parser.parse_args()
