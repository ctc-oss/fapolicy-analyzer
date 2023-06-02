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

from fapolicy_analyzer.util.xdg_utils import (
    app_config_dir_prefix,
    app_data_dir_prefix,
    app_state_dir_prefix,
)


def test_app_state_dir_prefix():
    strBasename = "Arbitrary.txt"
    strHomeDir = os.environ.get("HOME")
    strStateDefaultDir = strHomeDir + "/.local/state/"
    strExpected = strStateDefaultDir + "fapolicy-analyzer/" + strBasename

    assert app_state_dir_prefix(strBasename) == strExpected


def test_app_data_dir_prefix():
    strBasename = "Arbitrary.txt"
    strHomeDir = os.environ.get("HOME")
    strDataDefaultDir = strHomeDir + "/.local/share/"
    strExpected = strDataDefaultDir + "fapolicy-analyzer/" + strBasename

    assert app_data_dir_prefix(strBasename) == strExpected


def test_app_config_dir_prefix():
    strBasename = "Arbitrary.txt"
    strHomeDir = os.environ.get("HOME")
    strConfigDefaultDir = strHomeDir + "/.config/"
    strExpected = strConfigDefaultDir + "fapolicy-analyzer/" + strBasename

    assert app_config_dir_prefix(strBasename) == strExpected


def test_app_state_dir_prefix_as_root(mocker):
    mocker.patch("os.geteuid", return_value=0)
    mocker.patch("os.path.exists", return_value=True)

    strBasename = "Arbitrary.txt"
    strExpected = os.path.join("/var", "lib", "fapolicy-analyzer/", strBasename)
    assert app_state_dir_prefix(strBasename) == strExpected


def test_app_data_dir_prefix_as_root(mocker):
    mocker.patch("os.geteuid", return_value=0)
    mocker.patch("os.path.exists", return_value=True)

    strBasename = "Arbitrary.txt"
    strExpected = os.path.join("/var", "log", "fapolicy-analyzer", strBasename)

    assert app_data_dir_prefix(strBasename) == strExpected


def test_app_config_dir_prefix_as_root(mocker):
    mocker.patch("os.geteuid", return_value=0)
    mocker.patch("os.path.exists", return_value=True)

    strBasename = "Arbitrary.txt"
    strExpected = os.path.join("/etc", "fapolicy-analyzer", strBasename)

    assert app_config_dir_prefix(strBasename) == strExpected
