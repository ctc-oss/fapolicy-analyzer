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

import gi
import pytest

import context  # noqa: F401

gi.require_version("Gtk", "3.0")
from unittest.mock import MagicMock

from fapolicy_analyzer.ui.add_file_button import AddFileButton
from gi.repository import Gtk


@pytest.fixture
def widget():
    return AddFileButton()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Button


def test_fires_files_added(widget, mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.add_file_button.Gtk.FileChooserDialog.run",
        return_value=Gtk.ResponseType.OK,
    )
    mocker.patch(
        "fapolicy_analyzer.ui.add_file_button.Gtk.FileChooserDialog.get_filenames",
        return_value=["foo"],
    )
    mocker.patch("fapolicy_analyzer.ui.add_file_button.path.isfile", return_value=True)
    mockHandler = MagicMock()
    widget.files_added += mockHandler
    addBtn = widget.get_ref()
    addBtn.set_parent(Gtk.Window())
    addBtn.clicked()
    mockHandler.assert_called_with(["foo"])


def test_fires_files_w_spaces_added(widget, mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.add_file_button.Gtk.FileChooserDialog.run",
        return_value=Gtk.ResponseType.OK,
    )
    mocker.patch(
        "fapolicy_analyzer.ui.add_file_button.Gtk.FileChooserDialog.get_filenames",
        return_value=["/tmp/a file name with spaces"],
    )
    mocker.patch("fapolicy_analyzer.ui.add_file_button.path.isfile", return_value=True)
    mocker.patch(
        "fapolicy_analyzer.ui.add_file_button.Gtk.MessageDialog.run",
        return_value=Gtk.ResponseType.OK,
    )
    mockHandler = MagicMock()
    widget.files_added += mockHandler
    addBtn = widget.get_ref()
    addBtn.set_parent(Gtk.Window())
    addBtn.clicked()
    assert (
        not mockHandler.called
    ), "Callback should not be invoked; Filepath w/spaces should be filtered out"
