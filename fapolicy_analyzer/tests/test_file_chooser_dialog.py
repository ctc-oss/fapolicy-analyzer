# Copyright Concurrent Technologies Corporation 2023
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

from fapolicy_analyzer.ui.file_chooser_dialog import FileChooserDialog

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


@pytest.fixture
def parent():
    return Gtk.Window()


def test_creates_dialog(parent):
    dialog = FileChooserDialog(
        title="foo", parent=parent, do_overwrite_confirmation=True
    )
    assert isinstance(dialog, Gtk.FileChooserDialog)
    assert dialog.get_title() == "foo"
    assert dialog.get_transient_for() == parent
    assert dialog.get_do_overwrite_confirmation()


def test_get_filename(parent, mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.file_chooser_dialog.Gtk.FileChooserDialog.run",
        return_value=Gtk.ResponseType.OK,
    )
    mocker.patch(
        "fapolicy_analyzer.ui.add_file_button.Gtk.FileChooserDialog.get_filename",
        return_value="foo",
    )
    dialog = FileChooserDialog(title="", parent=parent)
    assert dialog.get_filename() == "foo"


def test_get_filename_cancel(parent, mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.file_chooser_dialog.Gtk.FileChooserDialog.run",
        return_value=Gtk.ResponseType.CANCEL,
    )
    dialog = FileChooserDialog(title="", parent=parent)
    assert dialog.get_filename() is None


def test_get_filenames(parent, mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.file_chooser_dialog.Gtk.FileChooserDialog.run",
        return_value=Gtk.ResponseType.OK,
    )
    mocker.patch(
        "fapolicy_analyzer.ui.add_file_button.Gtk.FileChooserDialog.get_filenames",
        return_value=["foo"],
    )
    dialog = FileChooserDialog(title="", parent=parent)
    assert dialog.get_filenames() == ["foo"]


def test_get_filenames_cancel(parent, mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.file_chooser_dialog.Gtk.FileChooserDialog.run",
        return_value=Gtk.ResponseType.CANCEL,
    )
    dialog = FileChooserDialog(title="", parent=parent)
    assert dialog.get_filenames() == []
