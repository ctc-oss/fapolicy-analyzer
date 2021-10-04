import context  # noqa: F401
import logging
import os
import sys
import shutil
import pytest
from unittest.mock import patch
from ui.session_manager import sessionManager
from ui.__main__ import main
from util.xdg_utils import xdg_state_dir_prefix


@pytest.fixture
def session():
    sessionManager.__init__()
    logging.root.setLevel(logging.WARNING)
    yield sessionManager

    # Reset global objects because they persist between tests.
    sessionManager.__init__()
    logging.root.setLevel(logging.WARNING)


@pytest.fixture
def mocks(mocker):
    mocker.patch("ui.__main__.MainWindow")
    mocker.patch("ui.__main__.Gtk")


@pytest.mark.usefixtures("mocks", "session")
def test_parse_args_no_options():
    testargs = ["prog"]
    _home = os.path.expanduser("~")
    xdg_state_home = os.path.join(_home, ".local", "state")
    expectTmpPath = xdg_state_home + "/fapolicy-analyzer/FaCurrentSession.tmp"
    with patch.object(sys, "argv", testargs):
        main()

        assert logging.getLogger().level == logging.WARNING
        assert not sessionManager._SessionManager__bAutosaveEnabled
        assert sessionManager._SessionManager__iTmpFileCount == 2
        assert sessionManager._SessionManager__tmpFileBasename == expectTmpPath

        # Tear down
        shutil.rmtree(xdg_state_home + "/fapolicy-analyzer/")


@pytest.mark.usefixtures("mocks", "session")
def test_parse_args_no_options_w_xdg_env():
    testargs = ["prog"]
    xdg_state_home = "/tmp"
    expectTmpPath = xdg_state_home + "/fapolicy-analyzer/FaCurrentSession.tmp"

    with patch.object(sys, "argv", testargs):
        os.environ["XDG_STATE_HOME"] = xdg_state_home
        main()

        assert logging.getLogger().level == logging.WARNING
        assert not sessionManager._SessionManager__bAutosaveEnabled
        assert sessionManager._SessionManager__iTmpFileCount == 2
        assert sessionManager._SessionManager__tmpFileBasename == expectTmpPath
        del os.environ["XDG_STATE_HOME"]

        # Tear down
        shutil.rmtree(xdg_state_home + "/fapolicy-analyzer/")


@pytest.mark.usefixtures("mocks", "session")
def test_parse_args_all_options():
    testargs = ["prog", "-v", "-a", "-s", "/tmp/TmpFileTemplate.tmp", "-c", "3"]
    with patch.object(sys, "argv", testargs):
        main()

        assert logging.getLogger().level == logging.DEBUG
        assert sessionManager._SessionManager__bAutosaveEnabled
        assert sessionManager._SessionManager__iTmpFileCount == 3
        assert (
            sessionManager._SessionManager__tmpFileBasename
            == "/tmp/TmpFileTemplate.tmp"
        )


@pytest.mark.usefixtures("mocks", "session")
def test_parse_args_all_options_w_xdg_env():
    """The '-s' option should overide the XDG_STATE_HOME env"""
    testargs = ["prog", "-v", "-a", "-s", "/tmp/TmpFileTemplate.tmp", "-c", "3"]

    with patch.object(sys, "argv", testargs):
        os.environ["XDG_STATE_HOME"] = "/tmp"
        main()

        assert logging.getLogger().level == logging.DEBUG
        assert sessionManager._SessionManager__bAutosaveEnabled
        assert sessionManager._SessionManager__iTmpFileCount == 3
        assert (
            sessionManager._SessionManager__tmpFileBasename
            == "/tmp/TmpFileTemplate.tmp"
        )
        del os.environ["XDG_STATE_HOME"]


@pytest.mark.usefixtures("session")
def test_main_no_options(mocker):
    testargs = ["prog"]
    testargs = ["prog"]
    _home = os.path.expanduser("~")
    xdg_state_home = os.path.join(_home, ".local", "state")
    expectTmpPath = xdg_state_home + "/fapolicy-analyzer/FaCurrentSession.tmp"

    with patch.object(sys, "argv", testargs):
        mockMW = mocker.patch("ui.__main__.MainWindow")
        mockGtk = mocker.patch("ui.__main__.Gtk")
        main()

        assert logging.getLogger().level == logging.WARNING
        assert not sessionManager._SessionManager__bAutosaveEnabled
        assert sessionManager._SessionManager__iTmpFileCount == 2
        assert sessionManager._SessionManager__tmpFileBasename == expectTmpPath
        mockMW.assert_called_once()
        mockGtk.main.assert_called_once()

        # Tear down
        shutil.rmtree(xdg_state_home + "/fapolicy-analyzer/")


@pytest.mark.usefixtures("session")
def test_main_all_options(mocker):
    """As above, the '-s' option should overide the XDG_STATE_HOME env"""
    testargs = ["prog", "-v", "-a", "-s", "/tmp/TmpFileTemplate.tmp", "-c", "3"]

    with patch.object(sys, "argv", testargs):
        mockMW = mocker.patch("ui.__main__.MainWindow")
        mockGtk = mocker.patch("ui.__main__.Gtk")
        main()

        assert logging.getLogger().level == logging.DEBUG
        assert sessionManager._SessionManager__bAutosaveEnabled
        assert sessionManager._SessionManager__iTmpFileCount == 3
        assert (
            sessionManager._SessionManager__tmpFileBasename
            == "/tmp/TmpFileTemplate.tmp"
        )
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
    os.environ["XDG_STATE_HOME"] = "/tmp"
    expectedFullPath = "/tmp/fapolicy-analyzer/FapTestTmp"
    generatedFullPath = xdg_state_dir_prefix("FapTestTmp")
    del os.environ["XDG_STATE_HOME"]

    assert expectedFullPath == generatedFullPath
