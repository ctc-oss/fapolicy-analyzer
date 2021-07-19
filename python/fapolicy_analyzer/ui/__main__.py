import gi
import logging
logging.basicConfig(level=logging.WARNING)
import argparse

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .main_window import MainWindow

# Globals
gbVerbose = False

def parse_cmdline():
    global gbVerbose

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose mode")
    args = parser.parse_args()

    # Set Verbosity Level
    gbVerbose = args.verbose
    if gbVerbose:
        logging.root.setLevel(logging.DEBUG)
        logging.debug("Verbosity enabled.")

def main():
    parse_cmdline()
    main = MainWindow()
    Gtk.main()

if __name__ == "__main__":
    main()
