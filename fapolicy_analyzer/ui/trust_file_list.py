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

from concurrent.futures import ThreadPoolExecutor
from time import localtime, mktime, strftime, strptime

import fapolicy_analyzer.ui.strings as strings
import gi

from .configs import Colors
from .searchable_list import SearchableList
from .strings import FILE_LABEL, FILES_LABEL

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk  # isort: skip

# global variable used for stopping the running executor from call for UI
# updates if the widget was destroyed
_executorCanceled = False


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
        global _executorCanceled

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
            selection_type="multi",
        )
        self.trust_func = trust_func
        self.markup_func = markup_func
        self.__executor = ThreadPoolExecutor(max_workers=1)
        _executorCanceled = False
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

    def _update_tree_count(self, count):
        label = FILE_LABEL if count == 1 else FILES_LABEL
        self.treeCount.set_text(" ".join([str(count), label]))

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
        global _executorCanceled
        _executorCanceled = True
        self.__executor.shutdown()
        return False

    def refresh(self):
        self.trust_func()

    def load_trust(self, trust):
        def process():
            global _executorCanceled
            store = Gtk.ListStore(str, str, str, object, str, str)
            for i, data in enumerate(trust):
                status, bg_color, txt_color, date_time = self._base_row_data(data)
                store.append([status, date_time, data.path, data, bg_color, txt_color])

                if _executorCanceled:
                    return

            if not _executorCanceled:
                GLib.idle_add(self.load_store, store)

        self.set_loading(True)
        self.__executor.submit(process)
