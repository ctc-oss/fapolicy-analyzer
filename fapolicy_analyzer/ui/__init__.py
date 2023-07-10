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


import locale
import logging
import os
import sys
from typing import Dict, Optional, Sequence, Tuple

import gi
import pkg_resources
from fapolicy_analyzer.ui.strings import (
    RESOURCE_LOAD_FAILURE_DIALOG_ADD_TEXT,
    RESOURCE_LOAD_FAILURE_DIALOG_TEXT,
)

try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip

DOMAIN = "fapolicy_analyzer"
locale.setlocale(locale.LC_ALL, locale.getlocale())
locale_path = pkg_resources.resource_filename("fapolicy_analyzer", "locale")
locale.bindtextdomain(DOMAIN, locale_path)
locale.textdomain(DOMAIN)

_RESOURCES: Dict[str, str] = {}

_RESOURCE_PKG_TYPES = {
    "fapolicy_analyzer.glade": [".glade"],
    "fapolicy_analyzer.css": [".css"],
    "fapolicy_analyzer.resources": [".json"],
}


def _read_resource(package: str, name: str) -> Optional[Tuple[str, str]]:
    with resources.path(package, name) as path:
        if os.path.isfile(path):
            try:
                _file = open(path, "r")
                return (name, _file.read())
            except Exception as ex:
                logging.warning(f"Unable to read resource {name}")
                logging.debug(f"Error loading resource {name}", ex)
            finally:
                if _file:
                    _file.close()

    return None


def _read_resources(
    package: str, file_exts: Sequence[str] = []
) -> Sequence[Tuple[str, str]]:
    try:
        resource_names = [
            n
            for n in resources.contents(package)
            if not file_exts or os.path.splitext(n)[-1] in file_exts
        ]
    except Exception as ex:
        logging.warning(f"Unable to read resource from package {package}")
        logging.debug(f"Error reading resource contents for package {package}", ex)
        return []

    data_pairs = [_read_resource(package, n) for n in resource_names]
    return [d for d in data_pairs if d]


def _show_error_dialog():
    dialog = Gtk.MessageDialog(
        flags=0,
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text=RESOURCE_LOAD_FAILURE_DIALOG_TEXT,
    )
    dialog.format_secondary_text(RESOURCE_LOAD_FAILURE_DIALOG_ADD_TEXT)
    dialog.run()
    dialog.destroy()


def load_resources():
    global _RESOURCES
    for package, types in _RESOURCE_PKG_TYPES.items():
        _RESOURCES = {
            **_RESOURCES,
            **dict(_read_resources(package, types)),
        }

    if not _RESOURCES:
        _show_error_dialog()
        sys.exit(1)


def get_resource(name: str) -> str:
    return _RESOURCES.get(name, "")
