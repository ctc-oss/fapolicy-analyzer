# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
#
#
# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
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
