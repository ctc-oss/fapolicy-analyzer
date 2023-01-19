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

from typing import Any

import gi

gi.require_version("Gtk", "3.0")
from events import Events
from gi.repository import Gtk, Gdk

from fapolicy_analyzer.ui.loader import Loader
from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget


class SearchableList(UIBuilderWidget, Events):
    __events__ = ["selection_changed"]

    def __init__(
        self,
        columns,
        *actionButtons,
        searchColumnIndex=0,
        defaultSortIndex=0,
        defaultSortDirection=Gtk.SortType.DESCENDING,
        view_headers_visible=True,
        selection_type="single",
    ):
        UIBuilderWidget.__init__(self, "searchable_list")
        Events.__init__(self)

        self.searchColumnIndex = searchColumnIndex
        self.defaultSortIndex = defaultSortIndex
        self.defaultSortDirection = defaultSortDirection
        self.treeCount = self.get_object("treeCount")
        self.treeView = self.get_object("treeView")
        self.treeView.set_headers_visible(view_headers_visible)
        for column in columns:
            self.treeView.append_column(column)

        if selection_type == "multi":
            self.treeSelection = self.get_object("treeSelection")
            self.treeSelection.set_mode(Gtk.SelectionMode.MULTIPLE)
            self.treeView.set_rubber_banding(True)

        self.search = self.get_object("search")
        self.viewSwitcher = self.get_object("viewStack")
        self.viewSwitcher.add_named(Loader().get_ref(), "loader")
        self.set_action_buttons(*actionButtons)

    def __filter_view(self, model, iter, data):
        filter = self.get_object("search").get_text()
        return True if not filter else filter in model[iter][self.searchColumnIndex]

    def __get_tree_count(self):
        return self.treeViewFilter.iter_n_children(None)

    def _load_data(self):
        pass

    def _update_tree_count(self, count):
        self.treeCount.set_text(str(count))

    def load_store(self, store, **kwargs):
        def apply_prev_sort(model):
            currentModel = self.treeView.get_model()
            currentSort = (
                currentModel.get_sort_column_id()
                if currentModel
                else (self.defaultSortIndex, 0)
            )
            model.set_sort_column_id(*currentSort)
            return model

        self.treeViewFilter = store.filter_new()
        self.treeViewFilter.set_visible_func(self.__filter_view)

        sortableModel = apply_prev_sort(Gtk.TreeModelSort(model=self.treeViewFilter))
        self.treeView.set_model(sortableModel)
        if self.treeView.get_selection():
            self.treeView.get_selection().connect(
                "changed", self.on_view_selection_changed
            )
        self._update_tree_count(self.__get_tree_count())
        self.set_loading(False)

    def set_loading(self, loading):
        if loading:
            self.viewSwitcher.set_visible_child_name("loader")
            self.search.set_sensitive(False)
        else:
            self.viewSwitcher.set_visible_child_name("treeView")
            self.search.set_sensitive(True)

    def refresh(self):
        self._load_data()

    def set_action_buttons(self, *buttons):
        buttonGroup = self.get_object("actionButtons")

        # remove all buttons
        buttonGroup.foreach(lambda btn: buttonGroup.remove(btn))

        if not buttons:
            buttonGroup.hide()
            return

        for button in buttons:
            buttonGroup.pack_start(button, False, True, 0)
            buttonGroup.show_all()

    def get_action_buttons(self):
        return self.get_object("actionButtons").get_children()

    def select_rows(self, *paths):
        selection = self.treeView.get_selection()
        for p in paths:
            selection.select_path(p)

    def unselect_all_rows(self):
        self.treeView.get_selection().unselect_all()

    def find_selected_row_by_data(
        self, column_data: Any, data_index: int
    ) -> Gtk.TreePath:
        def search(model, path, iter, *_):
            nonlocal selected
            if model[iter][data_index] == column_data:
                selected = path
            return selected is not None

        selected = None
        self.treeView.get_model().foreach(
            search
        ) if self.treeView.get_model() is not None else None
        return selected

    def on_view_selection_changed(self, selection):
        model, treeiter = selection.get_selected_rows()
        data = [model[i] for i in treeiter] if model and treeiter else []
        self.selection_changed(data)

    def __refilter(self):
        self.treeViewFilter.refilter()
        self._update_tree_count(self.__get_tree_count())

    def on_search_activate(self, *args):
        self.__refilter()   
 
    def on_search_icon_release(self, *args):
        self.search.set_text("")
        self.__refilter()
