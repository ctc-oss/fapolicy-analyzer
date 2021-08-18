import context  # noqa: F401
import gi
import pytest

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ui.acl_list import ACLList


@pytest.fixture
def widget():
    return ACLList()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_loads_store(widget):
    users = [{"id": 1, "name": "baz"}, {"id": 2, "name": "foo"}]
    widget.load_store(users)
    view = widget.get_object("treeView")
    assert [u.get("name") for u in users] == [x[0] for x in view.get_model()]
    assert [u.get("id") for u in users] == [x[1] for x in view.get_model()]


def test_update_tree_count():
    widget = ACLList(label="foo", label_plural="foos")
    widget.load_store([{"id": 1, "name": "foo"}])
    label = widget.get_object("treeCount")
    assert label.get_text() == "1 foo"

    widget.load_store([{"id": 1, "name": "foo"}, {"id": 2, "name": "baz"}])
    label = widget.get_object("treeCount")
    assert label.get_text() == "2 foos"
