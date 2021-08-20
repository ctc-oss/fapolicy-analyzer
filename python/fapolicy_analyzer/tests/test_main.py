import context  # noqa: F401
import logging
import os
import sys
import shutil
import pytest
from unittest.mock import patch
from ui.state_manager import stateManager
from ui.__main__ import parse_cmdline, main
from util.xdg_utils import xdg_state_dir_prefix


@pytest.fixture
def state():
    stateManager.__init__()
    logging.root.setLevel(logging.WARNING)
    yield stateManager

    # Reset global objects because they persist between tests.
    stateManager.__init__()
    logging.root.setLevel(logging.WARNING)


def test_parse_args_no_options(mocker, state):
    testargs = ["prog"]
    _home = os.path.expanduser('~')
    xdg_state_home = os.path.join(_home, '.local', 'state')
    expectTmpPath = xdg_state_home + "/fapolicy-analyzer/FaCurrentSession.tmp"
    with patch.object(sys, 'argv', testargs):
        parse_cmdline()

        assert logging.getLogger().level == logging.WARNING
        assert not stateManager._StateManager__bAutosaveEnabled
        assert stateManager._StateManager__iTmpFileCount == 2
        assert stateManager._StateManager__tmpFileBasename == expectTmpPath

        # Tear down
        shutil.rmtree(xdg_state_home + "/fapolicy-analyzer/")


def test_parse_args_no_options_w_xdg_env(mocker, state):
    testargs = ["prog"]
    xdg_state_home = "/tmp"
    expectTmpPath = xdg_state_home + "/fapolicy-analyzer/FaCurrentSession.tmp"

    with patch.object(sys, 'argv', testargs):
        os.environ['XDG_STATE_HOME'] = xdg_state_home
        parse_cmdline()

        assert logging.getLogger().level == logging.WARNING
        assert not stateManager._StateManager__bAutosaveEnabled
        assert stateManager._StateManager__iTmpFileCount == 2
        assert stateManager._StateManager__tmpFileBasename == expectTmpPath
        del os.environ['XDG_STATE_HOME']

        # Tear down
        shutil.rmtree(xdg_state_home + "/fapolicy-analyzer/")


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
        # No teardown because we are using a system dir


def test_parse_args_all_options_w_xdg_env(mocker, state):
    """The '-s' option should overide the XDG_STATE_HOME env"""
    testargs = ["prog",
                "-v",
                "-a",
                "-s", "/tmp/TmpFileTemplate.tmp",
                "-c", "3"]

    with patch.object(sys, 'argv', testargs):
        os.environ['XDG_STATE_HOME'] = '/tmp'
        parse_cmdline()

        assert logging.getLogger().level == logging.DEBUG
        assert stateManager._StateManager__bAutosaveEnabled
        assert stateManager._StateManager__iTmpFileCount == 3
        assert stateManager._StateManager__tmpFileBasename == "/tmp/TmpFileTemplate.tmp"
        del os.environ['XDG_STATE_HOME']


def test_main_no_options(mocker, state):
    testargs = ["prog"]
    testargs = ["prog"]
    _home = os.path.expanduser('~')
    xdg_state_home = os.path.join(_home, '.local', 'state')
    expectTmpPath = xdg_state_home + "/fapolicy-analyzer/FaCurrentSession.tmp"

    with patch.object(sys, 'argv', testargs):
        mockMW = mocker.patch("ui.__main__.MainWindow")
        mockGtk = mocker.patch("ui.__main__.Gtk")
        main()

        assert logging.getLogger().level == logging.WARNING
        assert not stateManager._StateManager__bAutosaveEnabled
        assert stateManager._StateManager__iTmpFileCount == 2
        assert stateManager._StateManager__tmpFileBasename == expectTmpPath
        mockMW.assert_called_once()
        mockGtk.main.assert_called_once()

        # Tear down
        shutil.rmtree(xdg_state_home + "/fapolicy-analyzer/")


def test_main_all_options(mocker, state):
    """As above, the '-s' option should overide the XDG_STATE_HOME env"""
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


def test_xdg_state_dir_prefix_w_exception(mocker):
    """Simulate a directory creation failure to execute the exception
    handling code.
    """
    mockMakeDirs = mocker.patch("os.makedirs", side_effect=IOError)
    generatedFullPath = xdg_state_dir_prefix("FapTestTmp")
    mockMakeDirs.assert_called()
    assert generatedFullPath == "/tmp/FapTestTmp"


def test_xdg_state_dir_prefix_w_xdg_env():
    try:
        os.environ['XDG_STATE_HOME'] = '/tmp'
        expectedFullPath = '/tmp/fapolicy-analyzer/FapTestTmp'
        generatedFullPath = xdg_state_dir_prefix("FapTestTmp")
        del os.environ['XDG_STATE_HOME']
    except Exception as e:
        print(e)

    assert expectedFullPath == generatedFullPath
