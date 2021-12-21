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

import fapolicy_analyzer.ui.strings as strings
import gi

gi.require_version("Gtk", "3.0")
from concurrent.futures import ThreadPoolExecutor
from time import localtime, mktime, strftime, strptime

from gi.repository import GLib, Gtk

from .searchable_list import SearchableList
from .strings import FILE_LABEL, FILES_LABEL

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
            self._columns(), *args, searchColumnIndex=2, defaultSortIndex=2
        )
        self.trust_func = trust_func
        self.markup_func = markup_func
        self.__executor = ThreadPoolExecutor(max_workers=1)
        _executorCanceled = False
        self.refresh()
        self.selection_changed += self.__handle_selection_changed
        self.get_ref().connect("destroy", self.on_destroy)

    def __handle_selection_changed(self, data):
        if data:
            trust = [datum[3] for datum in data]
        else:
            trust = None
        self.trust_selection_changed(trust)

    def _columns(self):
        # trust status column
        trustColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_TRUST_HEADER,
            Gtk.CellRendererText(background="light gray"),
            markup=0,
        )
        trustColumn.set_sort_column_id(0)

        # modification time column
        mtimeColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_MTIME_HEADER,
            Gtk.CellRendererText(),
            text=1,
            cell_background=4,
        )
        mtimeColumn.set_sort_column_id(1)

        # fullpath column
        fileColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_FILE_HEADER,
            Gtk.CellRendererText(),
            text=2,
            cell_background=4,
        )
        fileColumn.set_sort_column_id(2)
        return [trustColumn, mtimeColumn, fileColumn]

    def _update_tree_count(self, count):
        label = FILE_LABEL if count == 1 else FILES_LABEL
        self.treeCount.set_text(" ".join([str(count), label]))

    def on_destroy(self, *args):
        global _executorCanceled
        _executorCanceled = True
        self.__executor.shutdown(cancel_futures=True)
        return False

    def refresh(self):
        self.trust_func()

    def load_trust(self, trust):
        def process():
            global _executorCanceled
            store = Gtk.ListStore(str, str, str, object, str)
            for i, data in enumerate(trust):
                status, *rest = (
                    self.markup_func(data.status)
                    if self.markup_func
                    else (data.status,)
                )
                bgColor = rest[0] if rest else "white"
                secsEpoch = data.actual.last_modified if data.actual else None
                strDateTime = epoch_to_string(secsEpoch)

                store.append([status, strDateTime, data.path, data, bgColor])

                if _executorCanceled:
                    return

            if not _executorCanceled:
                GLib.idle_add(self.load_store, store)

        self.set_loading(True)
        self.__executor.submit(process)
