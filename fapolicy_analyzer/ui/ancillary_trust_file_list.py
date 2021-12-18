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

import gi
import fapolicy_analyzer.ui.strings as strings

gi.require_version("Gtk", "3.0")
import os.path
from functools import reduce
from gi.repository import Gtk
from types import SimpleNamespace
from .configs import Colors
from .add_file_button import AddFileButton
from .trust_file_list import TrustFileList, epoch_to_string


class AncillaryTrustFileList(TrustFileList):
    def __init__(self, trust_func):
        addBtn = AddFileButton()
        addBtn.files_added += self.on_addBtn_files_added
        self._changesColumn = None
        self._changesetMap = self._changesets_to_map([])

        super().__init__(trust_func, self.__status_markup, addBtn.get_ref())

    def __status_markup(self, status):
        s = status.lower()
        return (
            ("<b><u>T</u></b>/D", Colors.LIGHT_GREEN)
            if s == "t"
            else ("T/<b><u>D</u></b>", Colors.LIGHT_RED)
            if s == "d"
            else ("T/D", Colors.ORANGE)
        )

    def _changesets_to_map(self, changesets):
        def reducer(map, path):
            map.get(changesetMap[path], []).append(path)
            return map

        # map change path to action, the action for the last change in the queue wins
        changesetMap = {
            p: a for e in changesets or [] for (p, a) in e.get_path_action_map().items()
        }
        return reduce(
            reducer,
            changesetMap,
            {"Add": [], "Del": []},
        )

    def _columns(self):
        self._changesColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_CHANGES_HEADER,
            Gtk.CellRendererText(background="light gray"),
            text=5,
        )
        self._changesColumn.set_sort_column_id(5)
        return [self._changesColumn, *super()._columns()]

    def set_changesets(self, changesets):
        self._changesetMap = self._changesets_to_map(changesets)

    def load_trust(self, trust):
        # Hide changes column if there are no changes
        self._changesColumn.set_visible(
            self._changesetMap["Add"] or self._changesetMap["Del"]
        )

        store = Gtk.ListStore(str, str, str, object, str, str)
        for i, data in enumerate(trust):
            status, *rest = self.markup_func(data.status)
            bgColor = rest[0] if rest else "white"
            changes = (
                strings.CHANGESET_ACTION_ADD
                if data.path in self._changesetMap["Add"]
                else ""
            )

            secsEpoch = data.actual.last_modified if data.actual else None
            strDateTime = epoch_to_string(secsEpoch)
            store.append([status, strDateTime, data.path, data, bgColor, changes])

        for pth in self._changesetMap["Del"]:
            secsEpoch = int(os.path.getmtime(pth)) if os.path.isfile(pth) else None
            strDateTime = epoch_to_string(secsEpoch)
            store.append(
                [
                    "T/D",
                    strDateTime,
                    pth,
                    SimpleNamespace(path=pth),
                    "white",
                    strings.CHANGESET_ACTION_DEL,
                ]
            )

        self.load_store(store)

    def on_addBtn_files_added(self, files):
        if files:
            self.files_added(files)
