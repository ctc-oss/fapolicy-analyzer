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


from typing import Sequence

import markdown2
from bs4 import BeautifulSoup


def parse_media_urls(html: str, filter: str) -> Sequence[str]:
    soup = BeautifulSoup(html, "html.parser")
    return [
        url
        for url in [img.get("src") for img in soup("img")]
        if url and url.startswith(filter)
    ]


def markdown_to_html(markdown_file: str) -> str:
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
