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

import os.path
from functools import reduce
from types import SimpleNamespace

import gi

import fapolicy_analyzer.ui.strings as strings
from fapolicy_analyzer.ui.add_file_button import AddFileButton
from fapolicy_analyzer.ui.changeset_wrapper import TrustChangeset
from fapolicy_analyzer.ui.configs import Colors
from fapolicy_analyzer.ui.trust_file_list import TrustFileList, epoch_to_string

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


class AncillaryTrustFileList(TrustFileList):
    def __init__(self, trust_func):
        addBtn = AddFileButton()
        addBtn.files_added += self.on_addBtn_files_added
        self._changesColumn: Gtk.TreeViewColumn = None
        self._changesetMap = self._changesets_to_map([])

        super().__init__(trust_func, self.__status_markup, addBtn.get_ref())

    def __status_markup(self, status):
        s = status.lower()
        return (
            ("<b><u>T</u></b> / D", Colors.LIGHT_GREEN)
            if s == "t"
            else ("T / <b><u>D</u></b>", Colors.LIGHT_RED, Colors.WHITE)
            if s == "d"
            else ("T / D", Colors.ORANGE)
        )

    def _changesets_to_map(self, changesets):
        def reducer(map, path):
            map.get(changesetMap[path], []).append(path)
            return map

        # map change path to action, the action for the last change in the queue wins
        changesetMap = {
            p: a
            for e in changesets or []
            if isinstance(e, TrustChangeset)
            for (p, a) in e.serialize().items()
        }
        return reduce(
            reducer,
            changesetMap,
            {"Add": [], "Del": []},
        )

    def _columns(self):
        self._changesColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_CHANGES_HEADER,
            Gtk.CellRendererText(background=Colors.LIGHT_GRAY),
            text=6,
        )
        self._changesColumn.set_sort_column_id(6)
        return [self._changesColumn, *super()._columns()]

    def set_changesets(self, changesets):
        self._changesetMap = self._changesets_to_map(changesets)

    def init_list(self, count_of_trust_entries):
        store = Gtk.ListStore(str, str, str, object, str, str, str)
        self._load_trust(count_of_trust_entries, store)

    def _load_store(self, count_of_trust_entries, store):
        # Hide changes column if there are no changes
        self._changesColumn.set_visible(
            self._changesetMap["Add"] or self._changesetMap["Del"]
        )

        for pth in self._changesetMap["Del"]:
            file_exists = os.path.isfile(pth)
            status = "d" if file_exists else "u"
            data = SimpleNamespace(path=pth, status=status)
            secs_epoch = int(os.path.getmtime(pth)) if file_exists else None
            date_time = epoch_to_string(secs_epoch)
            store.append(
                [
                    "T/D",
                    date_time,
                    pth,
                    data,
                    Colors.WHITE,
                    Colors.BLACK,
                    strings.CHANGESET_ACTION_DEL,
                ]
            )

        super()._load_trust(count_of_trust_entries, store)

    def on_addBtn_files_added(self, files):
        if files:
            self.files_added(files)
