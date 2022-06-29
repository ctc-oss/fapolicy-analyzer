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
from events import Events
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from .configs import Colors
from .subject_list import SubjectList


class ObjectList(SubjectList, Events):
    def __init__(self):
        super().__init__()
        self.__events__ = [
            "file_selection_changed",
            "rule_view_activate",
        ]
        Events.__init__(self)
        self.reconcileContextMenu = self.__build_reconcile_context_menu()
        self.get_ref().set_name("objectList")

    def _columns(self):
        columns = super()._columns()
        modeCell = Gtk.CellRendererText(background=Colors.LIGHT_GRAY, xalign=0.5)
        modeColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_MODE_HEADER, modeCell, markup=6
        )
        modeColumn.set_sort_column_id(6)
        columns.insert(1, modeColumn)
        return columns

    def __markup(self, value, options, seperator=" / ", multiValue=False):
        def wrap(x):
            return f"<u><b>{x}</b></u>"
        valueSet = set(value.upper()) if multiValue else {value.upper()}
        matches = set(options).intersection(valueSet)
        return seperator.join([wrap(o) if o in matches else o for o in options])

    def __colors(self, access, mode):
        green = (Colors.LIGHT_GREEN, Colors.BLACK)
        orange = (Colors.ORANGE, Colors.BLACK)
        red = (Colors.LIGHT_RED, Colors.WHITE)
        if access.upper() != "A":
            return red

        numModes = len(set(mode.upper()).intersection({"R", "W", "X"}))
        return green if numModes == 3 else orange if numModes > 0 else red

    def __build_reconcile_context_menu(self):
        menu = Gtk.Menu()
        reconcileItem = Gtk.MenuItem.new_with_label("Reconcile File")
        reconcileItem.connect("activate", self.on_reconcile_file_activate)
        rulesItem = Gtk.MenuItem.new_with_label("Go To Rule")
        rulesItem.connect("activate", self.on_rule_menu_activate)
        menu.append(reconcileItem)
        menu.append(rulesItem)
        menu.show_all()
        return menu

    def on_rule_menu_activate(self, *args):
        model, path = self.get_object("treeView").get_selection().get_selected_rows()
        rule_id = model[0][7]
        self.rule_view_activate(rule_id = rule_id)

    def load_store(self, obj, **kwargs):
        if len(obj) > 0:
            objects, ids = obj

        else:
            objects = obj
            ids = []
        self._systemTrust = kwargs.get("systemTrust", [])
        self._ancillaryTrust = kwargs.get("ancillaryTrust", [])
        store = Gtk.ListStore(str, str, str, object, str, str, str, int)
        for o, i in zip(objects, ids):
            status = self._trust_markup(o)
            mode = self.__markup(
                o.mode.upper(),
                ["R", "W", "X"],
                seperator="",
                multiValue=True,
            )
            access = self.__markup(o.access.upper(), ["A", "D"])
            bg_color, txt_color = self.__colors(o.access, o.mode)
            store.append([status, access, o.file, o, bg_color, txt_color, mode, i])

        # call grandfather SearchableList's load_store method
        super(SubjectList, self).load_store(store)
