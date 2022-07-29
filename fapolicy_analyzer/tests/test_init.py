# Copyright Concurrent Technologies Corporation 2022
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

from importlib import reload
from unittest.mock import MagicMock

import fapolicy_analyzer.ui
import pytest
from callee.strings import StartsWith
from fapolicy_analyzer.ui import get_resource, load_resources


@pytest.fixture(autouse=True)
def reload_module():
    reload(fapolicy_analyzer.ui)


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("fapolicy_analyzer.ui.logging")


@pytest.fixture
def mock_sys_exit(mocker):
    return mocker.patch("fapolicy_analyzer.ui.sys.exit")


@pytest.fixture
def mock_error_dialog_run(mocker):
    return mocker.patch("fapolicy_analyzer.ui.Gtk.MessageDialog.run")


def test_load_resources():
    assert not fapolicy_analyzer.ui._RESOURCES
    load_resources()
    assert fapolicy_analyzer.ui._RESOURCES
    assert len(fapolicy_analyzer.ui._RESOURCES["main_window.glade"]) > 0


def test_load_resources_bad_package(mock_logger, mock_error_dialog_run, mock_sys_exit):
    fapolicy_analyzer.ui._RESOURCE_PKG_TYPES = {"bad.package": [".bar"]}
    load_resources()
    assert not fapolicy_analyzer.ui._RESOURCES
    mock_logger.warning.assert_called_with(
        "Unable to read resource from package bad.package"
    )
    mock_error_dialog_run.assert_called()
    mock_sys_exit.assert_called_with(1)


def test_load_resources_read_error(
    mock_logger, mock_error_dialog_run, mock_sys_exit, mocker
):
    mock_file = MagicMock(read=MagicMock(side_effect=Exception()))
    mocker.patch("builtins.open", return_value=mock_file)
    load_resources()
    mock_file.read.assert_called()
    mock_logger.warning.assert_called_with(StartsWith("Unable to read resource"))
    mock_error_dialog_run.assert_called()
    mock_sys_exit.assert_called_with(1)


def test_load_resources_bad_file(mock_error_dialog_run, mock_sys_exit, mocker):
    mock_open = mocker.patch("builtins.open")
    mocker.patch("fapolicy_analyzer.ui.resources.contents", return_value=["bad.file"])
    load_resources()
    mock_open.assert_not_called()
    mock_error_dialog_run.assert_called()
    mock_sys_exit.assert_called_with(1)


def test_get_resource():
    load_resources()
    data = get_resource("main_window.glade")
    assert len(data) > 0
