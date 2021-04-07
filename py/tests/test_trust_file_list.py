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
def trust_func():
    return MagicMock(
        return_value=[
            MagicMock(status="u", path="/tmp/foo"),
            MagicMock(status="t", path="/tmp/baz"),
        ]
    )


@pytest.fixture
def widget(trust_func):
    widget = TrustFileList(defaultLocation="/foo.db", trust_func=trust_func)
    refresh_gui()
    return widget


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


def test_uses_custom_trust_func(patch, trust_func):
    widget = TrustFileList(trust_func=trust_func)
    widget.databaseFileChooser.set_filename("/foo.db")
    refresh_gui()
    trust_func.assert_called_with("/foo.db")


def test_uses_custom_markup_func(patch):
    markup_func = MagicMock(return_value="t")
    widget = TrustFileList(markup_func=markup_func)
    widget.databaseFileChooser.set_filename("/foo")
    refresh_gui(0.2)
    markup_func.assert_called_with("trusted")


def test_sorting_path(patch, widget):
    trustView = widget.trustView
    assert ["/tmp/foo", "/tmp/baz"] == [x[1] for x in trustView.get_model()]
    trustView.get_column(1).clicked()
    assert ["/tmp/baz", "/tmp/foo"] == [x[1] for x in trustView.get_model()]


def test_sorting_status(patch, widget):
    trustView = widget.trustView
    assert ["u", "t"] == [x[0] for x in trustView.get_model()]
    trustView.get_column(0).clicked()
    assert ["t", "u"] == [x[0] for x in trustView.get_model()]


def test_filtering(patch, widget):
    trustView = widget.trustView
    trustViewFilter = widget.builder.get_object("trustViewSearch")
    trustViewFilter.set_text("foo")
    refresh_gui(0.2)
    paths = [x[1] for x in trustView.get_model()]
    assert "/tmp/foo" in paths
    assert "/tmp/baz" not in paths
