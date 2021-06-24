import context  # noqa: F401
import gi
import pytest

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ui.string_list import StringList


@pytest.fixture
def widget():
    return StringList()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_loads_store(widget):
    strings = ["foo", "baz"]
    widget.load_store(strings)
    view = widget.get_object("treeView")
    assert [s for s in strings] == [x[0] for x in view.get_model()]


def test_update_tree_count():
    widget = StringList(label="foo", label_plural="foos")
    widget.load_store([""])
    label = widget.get_object("treeCount")
    assert label.get_text() == "1 foo"

    widget.load_store(["", ""])
    label = widget.get_object("treeCount")
    assert label.get_text() == "2 foos"
