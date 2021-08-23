import logging

logging.basicConfig(level=logging.WARNING)
import argparse

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .main_window import MainWindow
from .state_manager import stateManager
from util.xdg_utils import xdg_state_dir_prefix


def parse_cmdline():
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
        stateManager.set_autosave_enable(args.autosave)

    # Enable edit session max autosave file count
    if args.count:
        stateManager.set_autosave_filecount(int(args.count))

    # Set Edit Session Tmp File
    if args.session:
        stateManager.set_autosave_filename(args.session)
    else:
        stateManager.set_autosave_filename(xdg_state_dir_prefix("FaCurrentSession.tmp"))


def main():
    parse_cmdline()
    MainWindow()
    Gtk.main()


if __name__ == "__main__":
    main()
