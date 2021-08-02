import context  # noqa: F401
import logging
import sys
import pytest
from unittest.mock import patch
from ui.state_manager import stateManager
from ui.__main__ import parse_cmdline, main


@pytest.fixture
def state():
    yield stateManager

    # Reset global objects because they persist between tests.
    stateManager.__init__()
    logging.root.setLevel(logging.WARNING)


def test_parse_args_no_options(mocker, state):
    testargs = ["prog"]
    with patch.object(sys, 'argv', testargs):
        parse_cmdline()

        assert logging.getLogger().level == logging.WARNING
        assert not stateManager._StateManager__bAutosaveEnabled
        assert stateManager._StateManager__iTmpFileCount == 2
        assert stateManager._StateManager__tmpFileBasename == "/tmp/FaCurrentSession.tmp"


def test_parse_args_all_options(mocker, state):
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


def test_main_no_options(mocker, state):
    testargs = ["prog"]

    with patch.object(sys, 'argv', testargs):
        mockMW = mocker.patch("ui.__main__.MainWindow")
        mockGtk = mocker.patch("ui.__main__.Gtk")
        main()

        assert logging.getLogger().level == logging.WARNING
        assert not stateManager._StateManager__bAutosaveEnabled
        assert stateManager._StateManager__iTmpFileCount == 2
        assert stateManager._StateManager__tmpFileBasename == "/tmp/FaCurrentSession.tmp"
        mockMW.assert_called_once()
        mockGtk.main.assert_called_once()


def test_main_all_options(mocker, state):
    testargs = ["prog",
                "-v",
                "-a",
                "-s", "/tmp/TmpFileTemplate.tmp",
                "-c", "3"]

    with patch.object(sys, 'argv', testargs):
        mockMW = mocker.patch("ui.__main__.MainWindow")
        mockGtk = mocker.patch("ui.__main__.Gtk")
        main()

        assert logging.getLogger().level == logging.DEBUG
        assert stateManager._StateManager__bAutosaveEnabled
        assert stateManager._StateManager__iTmpFileCount == 3
        assert stateManager._StateManager__tmpFileBasename == "/tmp/TmpFileTemplate.tmp"
        mockMW.assert_called_once()
        mockGtk.main.assert_called_once()
