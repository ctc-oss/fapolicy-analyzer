import context  # noqa: F401
import pytest
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock
from helpers import refresh_gui
from ui.trust_file_list import TrustFileList


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
    widget = TrustFileList(trust_func=trust_func)
    refresh_gui(1.5)
    return widget


def test_creates_widget(widget):
    assert type(widget.get_content()) is Gtk.Box


def test_uses_custom_trust_func(widget, trust_func):
    trust_func.assert_called()


def test_uses_custom_markup_func(trust_func):
    markup_func = MagicMock(return_value="t")
    TrustFileList(trust_func=trust_func, markup_func=markup_func)
    refresh_gui(1.5)
    markup_func.assert_called_with("t")


def test_sorting_path(widget):
    trustView = widget.trustView
    assert ["/tmp/foo", "/tmp/baz"] == [x[1] for x in trustView.get_model()]
    trustView.get_column(1).clicked()
    assert ["/tmp/baz", "/tmp/foo"] == [x[1] for x in trustView.get_model()]


def test_sorting_status(widget):
    trustView = widget.trustView
    assert ["u", "t"] == [x[0] for x in trustView.get_model()]
    trustView.get_column(0).clicked()
    assert ["t", "u"] == [x[0] for x in trustView.get_model()]


def test_filtering(widget):
    trustView = widget.trustView
    trustViewFilter = widget.builder.get_object("trustViewSearch")
    trustViewFilter.set_text("foo")
    refresh_gui(1.5)
    paths = [x[1] for x in trustView.get_model()]
    assert "/tmp/foo" in paths
    assert "/tmp/baz" not in paths
