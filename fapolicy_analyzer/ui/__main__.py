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

import logging

logging.basicConfig(level=logging.WARNING)
import argparse

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from fapolicy_analyzer.util.xdg_utils import xdg_state_dir_prefix
from fapolicy_analyzer import __version__ as app_version
from .session_manager import sessionManager
from .splash_screen import SplashScreen
from .store import init_store


def _parse_cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose mode"
    )
    parser.add_argument(
        "-a",
        "--autosave",
        action="store_true",
        help="Enable edit session autosave mode",
    )
    parser.add_argument(
        "-s", "--session", help="Specify edit session tmp file path/basename"
    )
    parser.add_argument(
        "-c", "--count", help="Specify the max number of session tmp files"
    )
    args = parser.parse_args()

    # Set Verbosity Level
    if args.verbose:
        logging.root.setLevel(logging.DEBUG)
        logging.debug("Verbosity enabled.")

    # Enable edit session autosaves
    if args.autosave:
        sessionManager.set_autosave_enable(args.autosave)

    # Enable edit session max autosave file count
    if args.count:
        sessionManager.set_autosave_filecount(int(args.count))

    # Set Edit Session Tmp File
    if args.session:
        sessionManager.set_autosave_filename(args.session)
    else:
        sessionManager.set_autosave_filename(
            xdg_state_dir_prefix("FaCurrentSession.tmp")
        )


def show_banner():
    print(f"fapolicy-analyzer v{app_version}")


def main():
    _parse_cmdline()
    show_banner()
    init_store()
    SplashScreen()
    Gtk.main()


if __name__ == "__main__":
    main()
