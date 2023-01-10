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
from fapolicy_analyzer.util.xdg_utils import (
    xdg_state_dir_prefix,
    xdg_data_dir_prefix,
)

gf_handler = logging.FileHandler(xdg_data_dir_prefix("fapolicy-analyzer.log"),
                                 mode="w")
gs_handler = logging.StreamHandler()
logging.basicConfig(level=logging.DEBUG, handlers=[gf_handler, gs_handler])
gs_handler.setLevel(logging.WARN)
gf_handler.setLevel(logging.WARN)

import argparse
import gi
from fapolicy_analyzer import __version__ as app_version
from fapolicy_analyzer.ui import load_resources
from fapolicy_analyzer.ui.session_manager import sessionManager
from fapolicy_analyzer.ui.splash_screen import SplashScreen
from fapolicy_analyzer.ui.store import init_store

gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "3.0")
from gi.repository import Gtk, GtkSource, GObject  # isort: skip


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
    parser.add_argument(
        "-l", "--loglevel",
        choices=["CRITICAL", "ERROR", "WARN", "INFO", "DEBUG"],
        help="Specify the log file leve. Default: WARN"
    )
    args = parser.parse_args()

    # Enable verbosity
    if args.verbose:
        gs_handler.setLevel(logging.INFO)
        logging.debug("Verbosity enabled.")

    # Enable edit session autosaves
    if args.autosave:
        sessionManager.set_autosave_enable(args.autosave)

    # Enable edit session max autosave file count
    if args.count:
        sessionManager.set_autosave_filecount(int(args.count))

    # Enable edit session max autosave file count
    if args.loglevel:
        dictOption2LogLevel = {"CRITICAL": logging.CRITICAL,
                               "ERROR": logging.ERROR,
                               "WARN": logging.WARN,
                               "INFO": logging.INFO,
                               "DEBUG": logging.DEBUG
                               }

        print(f"args.loglevel = {args.loglevel}")
        gf_handler.setLevel(dictOption2LogLevel[args.loglevel])

    # Set Edit Session Tmp File
    if args.session:
        sessionManager.set_autosave_filename(args.session)
    else:
        sessionManager.set_autosave_filename(
            xdg_state_dir_prefix("FaCurrentSession.tmp")
        )


def _register_types():
    GObject.type_register(GtkSource.View)


def show_banner():
    print(f"fapolicy-analyzer v{app_version}")


def main():
    _parse_cmdline()
    _register_types()
    load_resources()
    show_banner()
    init_store()
    SplashScreen()
    Gtk.main()


if __name__ == "__main__":
    main()
