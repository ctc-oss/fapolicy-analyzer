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

import os

import pytest

from fapolicy_analyzer.util.xdg_utils import (
    app_config_dir_prefix,
    app_data_dir_prefix,
    app_state_dir_prefix,
)


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
        return_value=os.path.join(_home, ".local", "share", fapa),
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
        return_value=os.path.join("/var", "lib", fapa),
    )
    mocker.patch(
        "fapolicy_analyzer.util.xdg_utils.app_config_dir",
        return_value=os.path.join("/etc", fapa),
    )


@pytest.mark.usefixtures("feature_xdg")
def test_app_state_dir_prefix_w_xdg():
    strBasename = "Arbitrary.txt"
    strHomeDir = os.environ.get("HOME")
    strStateDefaultDir = strHomeDir + "/.local/share/"
    strExpected = strStateDefaultDir + "fapolicy-analyzer/" + strBasename

    assert app_state_dir_prefix(strBasename) == strExpected


@pytest.mark.usefixtures("feature_xdg")
def test_app_data_dir_prefix_w_xdg():
    strBasename = "Arbitrary.txt"
    strHomeDir = os.environ.get("HOME")
    strDataDefaultDir = strHomeDir + "/.local/state/"
    strExpected = strDataDefaultDir + "fapolicy-analyzer/" + strBasename

    assert app_data_dir_prefix(strBasename) == strExpected


@pytest.mark.usefixtures("feature_xdg")
def test_app_config_dir_prefix_w_xdg():
    strBasename = "Arbitrary.txt"
    strHomeDir = os.environ.get("HOME")
    strConfigDefaultDir = strHomeDir + "/.config/"
    strExpected = strConfigDefaultDir + "fapolicy-analyzer/" + strBasename

    assert app_config_dir_prefix(strBasename) == strExpected


@pytest.mark.usefixtures("feature_no_xdg")
def test_app_state_dir_prefix_wo_xdg(mocker):
    mockMakeDirs = mocker.patch("fapolicy_analyzer.util.xdg_utils.os.makedirs")
    strBasename = "Arbitrary.txt"
    strStateDefaultDir = os.path.join("/var", "lib")
    strExpected = strStateDefaultDir + "/fapolicy-analyzer/" + strBasename

    assert app_state_dir_prefix(strBasename) == strExpected
    mockMakeDirs.assert_called()


@pytest.mark.usefixtures("feature_no_xdg")
def test_app_data_dir_prefix_wo_xdg(mocker):
    mockMakeDirs = mocker.patch("fapolicy_analyzer.util.xdg_utils.os.makedirs")
    strBasename = "Arbitrary.txt"
    strDataDefaultDir = os.path.join("/var", "log")
    strExpected = strDataDefaultDir + "/fapolicy-analyzer/" + strBasename

    assert app_data_dir_prefix(strBasename) == strExpected
    mockMakeDirs.assert_called()


@pytest.mark.usefixtures("feature_no_xdg")
def test_app_config_dir_prefix_wo_xdg(mocker):
    mockMakeDirs = mocker.patch("fapolicy_analyzer.util.xdg_utils.os.makedirs")
    strBasename = "Arbitrary.txt"
    strExpected = "/etc/fapolicy-analyzer/" + strBasename

    assert app_config_dir_prefix(strBasename) == strExpected
    mockMakeDirs.assert_called()
