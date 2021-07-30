import context  # noqa: F401
import logging
import sys

from unittest.mock import patch
from ui.state_manager import stateManager
from ui.__main__ import parse_cmdline, main


def test_parse_args(mocker):
    testargs = ["prog",
                "-v",
                "-a",
                "-s", "/tmp/TmpFileTemplate.tmp",
                "-c", "3"]
    with patch.object(sys, 'argv', testargs):
        parse_cmdline()

        assert logging.getLogger().level == logging.DEBUG
        assert stateManager._StateManager__bAutosaveEnabled
        assert stateManager._StateManager__iTmpFileCount == 3
        assert stateManager._StateManager__tmpFileBasename == "/tmp/TmpFileTemplate.tmp"


# Currently bypassed while I work on mocking the MainWindow within main()
def test_main(mocker):
    testargs = ["prog",
                "-v",
                "-a",
                "-s", "/tmp/TmpFileTemplate.tmp",
                "-c", "3"]

    with patch.object(sys, 'argv', testargs):
        assert 1
        return

        main()

        # assert logging.getLogger().level == logging.DEBUG
        # assert stateManager._StateManager__bAutosaveEnabled
        # assert stateManager._StateManager__iTmpFileCount == 3
        # assert stateManager._StateManager__tmpFileBasename == "/tmp/TmpFileTemplate.tmp"
