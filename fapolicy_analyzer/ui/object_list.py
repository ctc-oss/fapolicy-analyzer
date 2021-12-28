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
from gi.repository import Gtk

from .configs import Colors
from .subject_list import SubjectList


class ObjectList(SubjectList):

    def _columns(self):
        columns = super()._columns()
        modeCell = Gtk.CellRendererText()
        modeCell.set_property("background", "light gray")
        modeColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_MODE_HEADER, modeCell, markup=5
        )
        modeColumn.set_sort_column_id(5)
        columns.insert(1, modeColumn)
        return columns

    def __markup(self, value, options, seperator="/", multiValue=False):
        def wrap(x):
            return f"<b><u>{x}</u></b>"

        valueSet = set(value.upper()) if multiValue else {value.upper()}
        matches = set(options).intersection(valueSet)
        return seperator.join([wrap(o) if o in matches else o for o in options])

    def __color(self, access, mode):
        if access.upper() != "A":
            return Colors.LIGHT_RED

        numModes = len(set(mode.upper()).intersection({"R", "W", "X"}))
        return (
            Colors.LIGHT_GREEN
            if numModes == 3
            else Colors.ORANGE
            if numModes > 0
            else Colors.LIGHT_RED
        )

    def load_store(self, objects, **kwargs):
        self._systemTrust = kwargs.get("systemTrust", [])
        self._ancillaryTrust = kwargs.get("ancillaryTrust", [])
        store = Gtk.ListStore(str, str, str, object, str, str)
        for o in objects:
            status = self.__markup(o.trust.upper(), ["ST", "AT", "U"])
            mode = self.__markup(
                o.mode.upper(),
                ["R", "W", "X"],
                seperator="",
                multiValue=True,
            )
            access = self.__markup(o.access.upper(), ["A", "D"])
            bgColor = self.__color(o.access, o.mode)
            store.append([status, access, o.file, o, bgColor, mode])

        # call grandfather SearchableList's load_store method
        super(SubjectList, self).load_store(store)
