import context  # noqa: F401
import pytest
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock
from ui.trust_file_list import TrustFileList


_trust = [
    MagicMock(status="u", path="/tmp/foo"),
    MagicMock(status="t", path="/tmp/baz"),
]


def _trust_func(callback):
    callback(_trust)


@pytest.fixture
def widget():
    widget = TrustFileList(trust_func=_trust_func)
    return widget


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_uses_custom_trust_func():
    trust_func = MagicMock()
    TrustFileList(trust_func=trust_func)
    trust_func.assert_called()


def test_uses_custom_markup_func():
    markup_func = MagicMock(return_value="t")
    TrustFileList(trust_func=_trust_func, markup_func=markup_func)
    markup_func.assert_called_with("t")


def test_loads_trust_store(widget):
    widget.load_store(_trust)
    view = widget.get_object("treeView")
    assert [t.status for t in _trust] == [x[0] for x in view.get_model()]
    assert [t.path for t in _trust] == [x[1] for x in view.get_model()]


def test_fires_files_added(widget, mocker):
    mocker.patch(
        "ui.trust_file_list.Gtk.FileChooserDialog.run",
        return_value=Gtk.ResponseType.OK,
    )
    mocker.patch(
        "ui.trust_file_list.Gtk.FileChooserDialog.get_filenames",
        return_value=["foo"],
    )
    mocker.patch("ui.trust_file_list.path.isfile", return_value=True)
    mockHandler = MagicMock()
    widget.files_added += mockHandler
    parent = Gtk.Window()
    widget.get_ref().set_parent(parent)
    addBtn = widget.get_object("actionButtons").get_children()[0]
    addBtn.clicked()
    mockHandler.assert_called_with(["foo"])


def test_fires_files_w_spaces_added(widget, mocker):
    mocker.patch(
        "ui.trust_file_list.Gtk.FileChooserDialog.run",
        return_value=Gtk.ResponseType.OK,
    )
    mocker.patch(
        "ui.trust_file_list.Gtk.FileChooserDialog.get_filenames",
        return_value=["/tmp/a file name with spaces"],
    )
    mocker.patch("ui.trust_file_list.path.isfile", return_value=True)
    mocker.patch(
        "ui.trust_file_list.Gtk.MessageDialog.run",
        return_value=Gtk.ResponseType.OK,
    )
    mockHandler = MagicMock()
    widget.files_added += mockHandler
    parent = Gtk.Window()
    widget.get_ref().set_parent(parent)
    addBtn = widget.get_object("actionButtons").get_children()[0]
    addBtn.clicked()
    assert not mockHandler.called, "Callback should not be invoked; Filepath w/spaces should be filtered out"
