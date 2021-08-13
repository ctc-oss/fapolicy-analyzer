import logging
logging.basicConfig(level=logging.WARNING)
import argparse
import os

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .main_window import MainWindow
from .state_manager import stateManager


def XdgDirPrefix(strBaseName):
    """Prefixes the file basename, strBaseName, with the XDG_STATE_HOME
    directory, creates the directory if needed, and verifies that it is writable
    by the effective user
    """
    # Use the XDG_STATE_HOME env var, or $(HOME)/.local/state/
    _home = os.path.expanduser('~')
    xdg_state_home = os.environ.get('XDG_STATE_HOME',
                                    os.path.join(_home, '.local', 'state'))
    app_tmp_dir = xdg_state_home + "/fapolicy-analyzer/"

    try:
        # Create if needed, and verify writable dir
        if not os.path.exists(app_tmp_dir):
            print(" Creating '{}' ".format(app_tmp_dir))
            os.makedirs(app_tmp_dir, 0o700)
            os.access(app_tmp_dir, os.W_OK | os.X_OK)
    except Exception as e:
        print("Warning: Xdg directory creation of '{}' failed."
              "Using /tmp/".format(app_tmp_dir), e)
        app_tmp_dir = "/tmp/"

    return app_tmp_dir + strBaseName


def parse_cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose mode")
    parser.add_argument("-a", "--autosave", action="store_true",
                        help="Enable edit session autosave mode")
    parser.add_argument("-s", "--session",
                        help="Specify edit session tmp file path/basename")
    parser.add_argument("-c", "--count",
                        help="Specify the max number of session tmp files")
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
        stateManager.set_autosave_filename(XdgDirPrefix("FaCurrentSession.tmp"))


def main():
    parse_cmdline()
    MainWindow()
    Gtk.main()


if __name__ == "__main__":
    main()
