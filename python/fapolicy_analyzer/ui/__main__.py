import logging
logging.basicConfig(level=logging.WARNING)
import argparse

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .main_window import MainWindow
from .state_manager import stateManager

# Globals
gstrEditSessionTmpFile = "/tmp/FAPolicyToolSession.tmp.json"
gbAutosaveEnabled = False

def parse_cmdline():
    global gstrEditSessionTmpFile

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose mode")
    parser.add_argument("-a", "--autosave", action="store_true",
                        help="Enable edit session autosave mode")
    parser.add_argument("-s", "--session",
                        help="Specify edit session tmp file basename")
    args = parser.parse_args()

    # Set Verbosity Level
    if args.verbose:
        logging.root.setLevel(logging.DEBUG)
        logging.debug("Verbosity enabled.")

    # Enable edit session autosaves
    if args.autosave:
        gbAutosaveEnabled = True

    # Set Edit Session Tmp File
    if args.session:
        gstrEditSessionTmpFile = args.session


def main():
    parse_cmdline()
    MainWindow()
    stateManager.set_autosave_enable(gbAutosaveEnabled)
    Gtk.main()


if __name__ == "__main__":
    main()
