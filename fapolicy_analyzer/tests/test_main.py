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
import os
import shutil
import sys
from unittest.mock import patch

import pytest

from fapolicy_analyzer.ui.__main__ import main
from fapolicy_analyzer.ui.session_manager import sessionManager
from fapolicy_analyzer.util.xdg_utils import app_state_dir_prefix

import context  # noqa: F401


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
    mocker.patch("fapolicy_analyzer.ui.__main__.SplashScreen")
    mocker.patch("fapolicy_analyzer.ui.__main__.Gtk")
    mocker.patch("fapolicy_analyzer.ui.__main__.init_store")


@pytest.fixture
def feature_xdg(mocker):
    _home = os.path.expanduser("~")
    fapa = "fapolicy-analyzer"
    mocker.patch(
        "fapolicy_analyzer.util.xdg_utils.app_log_dir",
        return_value=os.path.join(_home, ".local", "state", fapa),
    )
    mocker.patch(
        "fapolicy_analyzer.util.xdg_utils.app_data_dir",
        return_value=os.path.join(_home, ".local", ".share", fapa),
    )
    mocker.patch(
        "fapolicy_analyzer.util.xdg_utils.app_config_dir",
        return_value=os.path.join(_home, ".config", fapa),
    )


@pytest.fixture
def feature_no_xdg(mocker):
    fapa = "fapolicy-analyzer"
    mocker.patch(
        "fapolicy_analyzer.util.xdg_utils.app_log_dir",
        return_value=os.path.join("/var", "log", fapa),
    )
    mocker.patch(
        "fapolicy_analyzer.util.xdg_utils.app_data_dir",
        return_value=os.path.join("/usr", "lib", fapa),
    )
    mocker.patch(
        "fapolicy_analyzer.util.xdg_utils.app_config_dir",
        return_value=os.path.join("/etc", fapa),
    )


@pytest.mark.usefixtures("mocks", "session", "feature_xdg")
def test_parse_args_no_options_w_xdg():
    """Create and use the ~/.local/ directory for tmp session files"""
    testargs = ["prog"]
    _home = os.path.expanduser("~")

    xdg_state_home = os.path.join(_home, ".local", ".share")
    expectTmpPath = xdg_state_home + "/fapolicy-analyzer/fapolicy-analyzer.tmp"
    with patch.object(sys, "argv", testargs):
        main()

        assert logging.getLogger().level == logging.WARNING
        assert not sessionManager._SessionManager__bAutosaveEnabled
        assert sessionManager._SessionManager__iTmpFileCount == 2
        assert sessionManager._SessionManager__tmpFileBasename == expectTmpPath

        # Tear down
        shutil.rmtree(xdg_state_home + "/fapolicy-analyzer/")


@pytest.mark.usefixtures("mocks", "session", "feature_no_xdg")
def test_parse_args_no_options_wo_xdg():
    """Attempt to create and use the /usr/lib/fapolicy-analyzer/ directory for
    tmp session files, however process does not have privileges. Fall back to
    /tmp/"""

    testargs = ["prog"]

    expectTmpPath = "/tmp/fapolicy-analyzer.tmp"
    with patch.object(sys, "argv", testargs):
        main()

        assert logging.getLogger().level == logging.WARNING
        assert not sessionManager._SessionManager__bAutosaveEnabled
        assert sessionManager._SessionManager__iTmpFileCount == 2
        assert sessionManager._SessionManager__tmpFileBasename == expectTmpPath


@pytest.mark.usefixtures("mocks", "session")
def test_parse_args_all_options():
    testargs = ["prog", "-v", "-a", "-s", "/tmp/TmpFileTemplate.tmp", "-c", "3"]
    with patch.object(sys, "argv", testargs):
        main()

        assert logging.getLogger().level == logging.WARNING
        assert sessionManager._SessionManager__bAutosaveEnabled
        assert sessionManager._SessionManager__iTmpFileCount == 3
        assert (
            sessionManager._SessionManager__tmpFileBasename
            == "/tmp/TmpFileTemplate.tmp"
        )


@pytest.mark.usefixtures("session", "feature_xdg")
def test_main_no_options_w_xdg(mocker):
    testargs = ["prog"]
    _home = os.path.expanduser("~")
    xdg_state_home = os.path.join(_home, ".local", ".share")
    expectTmpPath = xdg_state_home + "/fapolicy-analyzer/fapolicy-analyzer.tmp"

    with patch.object(sys, "argv", testargs):
        mockSplash = mocker.patch("fapolicy_analyzer.ui.__main__.SplashScreen")
        mockGtk = mocker.patch("fapolicy_analyzer.ui.__main__.Gtk")
        mockStore = mocker.patch("fapolicy_analyzer.ui.__main__.init_store")
        main()

        assert logging.getLogger().level == logging.WARNING
        assert not sessionManager._SessionManager__bAutosaveEnabled
        assert sessionManager._SessionManager__iTmpFileCount == 2
        assert sessionManager._SessionManager__tmpFileBasename == expectTmpPath
        mockSplash.assert_called_once()
        mockGtk.main.assert_called_once()
        mockStore.assert_called_once()

        # Tear down
        shutil.rmtree(xdg_state_home + "/fapolicy-analyzer/")


@pytest.mark.usefixtures("session", "feature_no_xdg")
def test_main_no_options_wo_xdg(mocker):
    """Attempt to create and use the /usr/lib/fapolicy-analyzer/ directory for
    tmp session files, however process does not have privileges. Fall back to
    /tmp/"""

    testargs = ["prog"]
    expectTmpPath = "/tmp/fapolicy-analyzer.tmp"

    with patch.object(sys, "argv", testargs):
        mockSplash = mocker.patch("fapolicy_analyzer.ui.__main__.SplashScreen")
        mockGtk = mocker.patch("fapolicy_analyzer.ui.__main__.Gtk")
        mockStore = mocker.patch("fapolicy_analyzer.ui.__main__.init_store")
        main()

        assert logging.getLogger().level == logging.WARNING
        assert not sessionManager._SessionManager__bAutosaveEnabled
        assert sessionManager._SessionManager__iTmpFileCount == 2
        assert sessionManager._SessionManager__tmpFileBasename == expectTmpPath
        mockSplash.assert_called_once()
        mockGtk.main.assert_called_once()
        mockStore.assert_called_once()


@pytest.mark.usefixtures("session")
def test_main_all_options(mocker):
    """As above, the '-s' option should overide the XDG_STATE_HOME env"""
    testargs = ["prog", "-v", "-a", "-s", "/tmp/TmpFileTemplate.tmp", "-c", "3"]

    with patch.object(sys, "argv", testargs):
        mockSplash = mocker.patch("fapolicy_analyzer.ui.__main__.SplashScreen")
        mockGtk = mocker.patch("fapolicy_analyzer.ui.__main__.Gtk")
        mockStore = mocker.patch("fapolicy_analyzer.ui.__main__.init_store")
        main()

        assert logging.getLogger().level == logging.WARNING
        assert sessionManager._SessionManager__bAutosaveEnabled
        assert sessionManager._SessionManager__iTmpFileCount == 3
        assert (
            sessionManager._SessionManager__tmpFileBasename
            == "/tmp/TmpFileTemplate.tmp"
        )
        mockSplash.assert_called_once()
        mockGtk.main.assert_called_once()
        mockStore.assert_called_once()


def test_xdg_state_dir_prefix_w_exception(mocker):
    """Simulate a directory creation failure to execute the exception
    handling code.
    """
    mocker.patch("os.path.exists", return_value=False)
    mockMakeDirs = mocker.patch("os.makedirs", side_effect=IOError)
    generatedFullPath = app_state_dir_prefix("FapTestTmp")
    mockMakeDirs.assert_called()
    assert generatedFullPath == "/tmp/FapTestTmp"
