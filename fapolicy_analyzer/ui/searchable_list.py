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

from fapolicy_analyzer.ui.strings import FILTERING_DISABLED_DURING_LOADING_MESSAGE

gi.require_version("Gtk", "3.0")
from events import Events
from gi.repository import Gtk

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

        def init_tree_view():
            tree_view = self.get_object("treeView")
            tree_selection = self.get_object("treeSelection")
            tree_view.set_headers_visible(view_headers_visible)
            for column in columns:
                tree_view.append_column(column)

            if selection_type == "multi":
                tree_selection.set_mode(Gtk.SelectionMode.MULTIPLE)
                tree_view.set_rubber_banding(True)

            return tree_view, tree_selection

        self.searchColumnIndex = searchColumnIndex
        self.defaultSortIndex = defaultSortIndex
        self.defaultSortDirection = defaultSortDirection
        self.treeCount = self.get_object("treeCount")
        self.treeView, self.treeSelection = init_tree_view()
        self.search = self.get_object("search")
        self.viewSwitcher = self.get_object("viewStack")
        self.viewSwitcher.add_named(Loader().get_ref(), "loader")
        self.view_container = self.get_object("viewContainer")
        self.progress_bar = self.get_object("progressBar")
        self.view_container.remove(
            self.progress_bar
        )  # progress bar only show when needed
        self.set_action_buttons(*actionButtons)

    def _filter_view(self, model, iter, data):
        filter = self.get_object("search").get_text()
        return True if not filter else filter in model[iter][self.searchColumnIndex]

    def _load_data(self):
        pass

    def _get_tree_count(self):
        return self.treeViewFilter.iter_n_children(None)

    def _update_list_status(self, status):
        self.treeCount.set_text(str(status))

    def _update_progress(self, progress_pct):
        def visible():
            return self.progress_bar in self.view_container.get_children()

        if progress_pct >= 100 or progress_pct < 0:
            if visible():
                self.view_container.remove(self.progress_bar)
            return

        if not visible():
            self.view_container.pack_start(self.progress_bar, False, True, 0)
            self.view_container.reorder_child(self.progress_bar, 1)
            self.view_container.show_all()

        self.progress_bar.set_fraction(progress_pct / 100)

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
        self.treeViewFilter.set_visible_func(self._filter_view)

        sortableModel = apply_prev_sort(Gtk.TreeModelSort(model=self.treeViewFilter))
        self.treeView.set_model(sortableModel)
        if self.treeView.get_selection():
            self.treeView.get_selection().connect(
                "changed", self.on_view_selection_changed
            )
        self._update_list_status(self._get_tree_count())
        self.set_loading(False)

    def set_loading(self, loading):
        if loading:
            self.viewSwitcher.set_visible_child_name("loader")
            self.search.set_sensitive(False)
            self.search.set_tooltip_text(FILTERING_DISABLED_DURING_LOADING_MESSAGE)
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

    def on_search_changed(self, search):
        self.treeViewFilter.refilter()
        self._update_list_status(self._get_tree_count())
