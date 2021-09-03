import context  # noqa: F401
import pytest
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock
from ui.add_file_button import AddFileButton


@pytest.fixture
def widget():
    return AddFileButton()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Button


def test_fires_files_added(widget, mocker):
    mocker.patch(
        "ui.add_file_button.Gtk.FileChooserDialog.run",
        return_value=Gtk.ResponseType.OK,
    )
    mocker.patch(
        "ui.add_file_button.Gtk.FileChooserDialog.get_filenames",
        return_value=["foo"],
    )
    mocker.patch("ui.add_file_button.path.isfile", return_value=True)
    mockHandler = MagicMock()
    widget.files_added += mockHandler
    addBtn = widget.get_ref()
    addBtn.set_parent(Gtk.Window())
    addBtn.clicked()
    mockHandler.assert_called_with(["foo"])


def test_fires_files_w_spaces_added(widget, mocker):
    mocker.patch(
        "ui.add_file_button.Gtk.FileChooserDialog.run",
        return_value=Gtk.ResponseType.OK,
    )
    mocker.patch(
        "ui.add_file_button.Gtk.FileChooserDialog.get_filenames",
        return_value=["/tmp/a file name with spaces"],
    )
    mocker.patch("ui.add_file_button.path.isfile", return_value=True)
    mocker.patch(
        "ui.add_file_button.Gtk.MessageDialog.run",
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
