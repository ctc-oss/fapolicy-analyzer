import context  # noqa: F401
import pytest
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from helpers import refresh_gui
from mocks import mock_System
from unittest.mock import MagicMock
from ui.trust_file_list import TrustFileList


@pytest.fixture
def patch(mocker):
    mocker.patch("ui.trust_file_list.System", return_value=mock_System())


@pytest.fixture
def widget(patch):
    return TrustFileList()


def test_creates_widget(widget):
    assert type(widget.get_content()) is Gtk.Box


def test_sets_defaultLocation(patch):
    widget = TrustFileList(
        locationAction=Gtk.FileChooserAction.SELECT_FOLDER, defaultLocation="/tmp/foo"
    )
    assert (
        widget.databaseFileChooser.get_action() == Gtk.FileChooserAction.SELECT_FOLDER
    )
    assert widget.databaseFileChooser.get_filename() == "/tmp/foo"


def test_uses_custom_trust_func(patch):
    trust_func = MagicMock()
    widget = TrustFileList(trust_func=trust_func)
    widget.databaseFileChooser.set_filename("/foo.db")
    refresh_gui(0.1)
    trust_func.assert_called_with("/foo.db")


def test_uses_custom_markup_func(patch):
    markup_func = MagicMock(return_value="t")
    widget = TrustFileList(markup_func=markup_func)
    widget.databaseFileChooser.set_filename("/foo")
    refresh_gui(0.2)
    markup_func.assert_called_with("trusted")
