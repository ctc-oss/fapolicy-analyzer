import context  # noqa: F401
import pytest
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock
from ui.trust_file_list import TrustFileList


_trust = [
    MagicMock(status="u", path="/tmp/bar"),
    MagicMock(status="t", path="/tmp/foo"),
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
    widget.load_trust(_trust)
    view = widget.get_object("treeView")
    assert [t.status for t in _trust] == [x[0] for x in view.get_model()]
    assert [t.path for t in _trust] == [x[1] for x in view.get_model()]


def test_fires_trust_selection_changed(widget):
    mockHandler = MagicMock()
    widget.trust_selection_changed += mockHandler
    view = widget.get_object("treeView")
    view.get_selection().select_path(Gtk.TreePath.new_first())
    mockHandler.assert_called_with(_trust[0])
