import logging
logging.basicConfig(level=logging.WARNING)
import argparse

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .main_window import MainWindow


def parse_cmdline():
    global gbVerbose

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose mode")
    args = parser.parse_args()

    # Set Verbosity Level
    if args.verbose:
        logging.root.setLevel(logging.DEBUG)
        logging.debug("Verbosity enabled.")


def main():
    parse_cmdline()
    MainWindow()
    Gtk.main()


if __name__ == "__main__":
    main()
