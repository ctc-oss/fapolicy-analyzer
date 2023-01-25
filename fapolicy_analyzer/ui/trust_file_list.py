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

import math
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Event
from time import localtime, mktime, strftime, strptime

import gi

import fapolicy_analyzer.ui.strings as strings
from fapolicy_analyzer.ui.configs import Colors
from fapolicy_analyzer.ui.searchable_list import SearchableList
from fapolicy_analyzer.ui.strings import (
    FILE_LABEL,
    FILES_LABEL,
    FILTERING_DISABLED_DURING_LOADING_MESSAGE,
)

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk  # isort: skip


def epoch_to_string(secsEpoch):
    if secsEpoch:
        # If last modified after midnight, display mtime, otherwise date
        # This strips off the hours, minutes, seconds to yield midnight 00:00:00
        timeMidnight = strptime(strftime("%d %b %y", localtime()), "%d %b %y")
        secsEpochMidnight = int(mktime(timeMidnight))

        if secsEpoch >= secsEpochMidnight:
            return strftime("%H:%M:%S", localtime(secsEpoch))
        else:
            return strftime("%Y-%m-%d", localtime(secsEpoch))
    else:
        return "Missing"


class TrustFileList(SearchableList):
    def __init__(self, trust_func, markup_func=None, *args):

        self.__events__ = [
            *super().__events__,
            "files_added",
            "files_deleted",
            "trust_selection_changed",
        ]

        super().__init__(
            self._columns(),
            *args,
            searchColumnIndex=2,
            defaultSortIndex=2,
            defaultSortDirection=Gtk.SortType.ASCENDING,
            selection_type="multi",
        )
        self.trust_func = trust_func
        self.markup_func = markup_func
        self.__executor = ThreadPoolExecutor(max_workers=100)
        self.__event = Event()
        self.refresh()
        self.selection_changed += self.__handle_selection_changed
        self.get_ref().connect("destroy", self.on_destroy)

    def __handle_selection_changed(self, data):
        trust = [datum[3] for datum in data] if data else None
        self.trust_selection_changed(trust)

    def _columns(self):
        def txt_color_func(col, renderer, model, iter, *args):
            color = model.get_value(iter, 5)
            renderer.set_property("foreground", color)

        # trust status column
        trustColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_TRUST_HEADER,
            Gtk.CellRendererText(background=Colors.LIGHT_GRAY, xalign=0.5),
            markup=0,
        )
        trustColumn.set_sort_column_id(0)

        # modification time column
        mtimeRenderer = Gtk.CellRendererText()
        mtimeColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_MTIME_HEADER,
            mtimeRenderer,
            text=1,
            cell_background=4,
        )
        mtimeColumn.set_cell_data_func(mtimeRenderer, txt_color_func)
        mtimeColumn.set_sort_column_id(1)

        # fullpath column
        fileRenderer = Gtk.CellRendererText()
        fileColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_FILE_HEADER,
            fileRenderer,
            text=2,
            cell_background=4,
        )
        fileColumn.set_cell_data_func(fileRenderer, txt_color_func)
        fileColumn.set_sort_column_id(2)
        return [trustColumn, mtimeColumn, fileColumn]

    def _update_list_status(self, count):
        label = FILE_LABEL if count == 1 else FILES_LABEL
        super()._update_list_status(" ".join([str(count), label]))

    def _update_loading_status(self, status):
        super()._update_list_status(status)

    def _base_row_data(self, data):
        status, *rest = (
            self.markup_func(data.status) if self.markup_func else (data.status,)
        )
        bg_color, *rest = rest if rest else (Colors.WHITE,)
        txt_color, *rest = rest if rest else (Colors.BLACK,)
        secs_epoch = data.actual.last_modified if data.actual else None
        date_time = epoch_to_string(secs_epoch)
        return status, bg_color, txt_color, date_time

    def on_destroy(self, *args):
        self.__event.set()
        self.__executor.shutdown()
        return False

    def refresh(self):
        self.trust_func()

    def load_trust(self, count_of_trust_entries):
        def process_rows(queue, total):
            store = self.treeViewFilter
            columns = range(6)
            for i in range(200):
                if not queue.empty() and not self.__event.is_set():
                    row = queue.get()
                    store.insert_with_valuesv(-1, columns, row)

            if self.__event.is_set():
                return False

            count = self._get_tree_count()
            total = 61000
            # print(f"count = {count}, total = {total}")
            if count < total:
                pct = math.ceil((count / total) * 100)
                self._update_loading_status(f"Loading trust {pct}% complete...")
                self._update_progress(pct)
                return True
            else:
                self.treeViewFilter = store.filter_new()
                self.treeViewFilter.set_visible_func(self._filter_view)
                self.treeView.set_model(self.treeViewFilter)
                self._update_list_status(self._get_tree_count())
                self._update_progress(100)
                self.search.set_sensitive(True)
                self.search.set_tooltip_text(None)
                return False

        store = Gtk.ListStore(str, str, str, object, str, str)
        self.__load_store(store)
        self.search.set_sensitive(False)
        self.search.set_tooltip_text(FILTERING_DISABLED_DURING_LOADING_MESSAGE)
        self.__queue = Queue()
        GLib.timeout_add(200, process_rows, self.__queue, count_of_trust_entries)

    def append_trust(self, trust, percent):
        def process_trust(trust):
            for data in trust:
                if self.__event.is_set():
                    return

                status, bg_color, txt_color, date_time = self._base_row_data(data)
                self.__queue.put(
                    [status, date_time, data.path, data, bg_color, txt_color]
                )

        if not self.__event.is_set():
            self.__executor.submit(process_trust, trust)

    def __load_store(self, store, **kwargs):
        store.set_sort_column_id(self.defaultSortIndex, self.defaultSortDirection)
        self.treeViewFilter = store
        self.treeView.set_model(self.treeViewFilter)
        if self.treeView.get_selection():
            self.treeView.get_selection().connect(
                "changed", self.on_view_selection_changed
            )
        self._update_loading_status("Loading trust 0% complete...")
        self.set_loading(False)
