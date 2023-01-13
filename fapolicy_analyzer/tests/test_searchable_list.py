# Copyright Concurrent Technologies Corporation 2021
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

import context  # noqa: F401 # isort: skip

from unittest.mock import MagicMock

import gi
import pytest
from callee import Contains
from fapolicy_analyzer.ui.searchable_list import SearchableList

from helpers import refresh_gui

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk # isort: skip


@pytest.fixture()
def widget():
    column = Gtk.TreeViewColumn("foo", Gtk.CellRendererText(), text=0)
    column.set_sort_column_id(0)
    widget = SearchableList([column], selection_type="multi")
    store = Gtk.ListStore(str)
    store.append(["baz"])
    store.append(["foo"])
    widget.load_store(store)
    return widget


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_adds_columns(widget):
    columns = widget.get_object("treeView").get_columns()
    assert columns[0].get_title() == "foo"


def test_adds_action_button():
    widget = SearchableList([], Gtk.Button(label="foo"))
    buttons = widget.get_object("actionButtons").get_children()
    assert buttons[0].get_label() == "foo"


def test_load_store(widget):
    store = Gtk.ListStore(str)
    store.append(["blah"])
    widget.load_store(store)
    view = widget.get_object("treeView")
    assert ["blah"] == [x[0] for x in view.get_model()]


def test_toggle_loader(widget):
    search = widget.get_object("search")
    viewSwitcher = widget.get_object("viewStack")
    assert search.get_sensitive()
    assert viewSwitcher.get_visible_child_name() == "treeView"

    widget.set_loading(True)
    assert not search.get_sensitive()
    assert viewSwitcher.get_visible_child_name() == "loader"

    widget.set_loading(False)
    assert search.get_sensitive()
    assert viewSwitcher.get_visible_child_name() == "treeView"


def test_fires_selection_changed_event(widget):
    mockHandler = MagicMock()
    widget.selection_changed += mockHandler
    view = widget.get_object("treeView")
    view.get_selection().select_path(Gtk.TreePath.new_first())
    mockHandler.assert_called_with([Contains("baz")])


def test_sorting(widget):
    view = widget.get_object("treeView")
    assert ["baz", "foo"] == [x[0] for x in view.get_model()]  # default sort
    view.get_column(0).clicked()
    assert ["foo", "baz"] == [x[0] for x in view.get_model()]  # new sort


def test_filtering(widget):
    view = widget.get_object("treeView")
    viewFilter = widget.get_object("search")
    viewFilter.set_text("foo")
    window = Gtk.Window()
    display = Gdk.Display.get_default()
    window.set_screen(display.get_screen(0))
    widget.get_ref().set_parent(window)
    window.present()
    window.show()
    event = Gdk.EventKey()
    event.window = window
    event.type = Gdk.EventType.KEY_PRESS
    event.send_event = True
    event.time = Gdk.CURRENT_TIME
    event.keyval = Gdk.keyval_from_name("Enter")
    event.put()
    refresh_gui(delay=0.3)
    paths = [x[0] for x in view.get_model()]
    assert "foo" in paths
    assert "baz" not in paths


def test_loads_data_on_refresh(widget, mocker):
    widget._load_data = MagicMock(side_effect=widget._load_data)
    widget.refresh()
    widget._load_data.assert_called()


def test_select_rows(widget):
    view = widget.get_object("treeView")
    assert view.get_selection().count_selected_rows() == 0

    expected_path = Gtk.TreePath.new_from_indices([1])
    widget.select_rows(expected_path)
    model, paths = view.get_selection().get_selected_rows()
    assert len(paths) == 1
    assert model.get_value(model.get_iter(paths[0]), 0) == "foo"


def test_unselect_all_rows(widget):
    view = widget.get_object("treeView")
    view.get_selection().select_all()
    assert view.get_selection().count_selected_rows() == 2
    widget.unselect_all_rows()
    assert view.get_selection().count_selected_rows() == 0


def test_find_selected_row_by_data(widget):
    view = widget.get_object("treeView")
    model = view.get_model()
    view.get_selection().select_path(Gtk.TreePath.new_from_indices([1]))
    actual_path = widget.find_selected_row_by_data("foo", 0)
    assert model.get_value(model.get_iter(actual_path), 0) == "foo"
