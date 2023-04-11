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

from fapolicy_analyzer import System, rules_difference
from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget
from fapolicy_analyzer.ui.searchable_list import SearchableList

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip

class RulesDifferenceDialog(UIBuilderWidget):
    def __init__(self, 
                 current_system: System,
                 previous_system: System,
                 parent=None,
    ):
        super().__init__()
        if parent:
            self.get_ref().set_transient_for(parent)

        diffs = rules_difference(previous_system, current_system).split("\n")
        new_list = SearchableList(self.__columns())
        prev_list = SearchableList(self.__columns())
        self.get_object("newContent").add(new_list.get_ref())
        self.get_object("prevContent").add(prev_list.get_ref())
        new_store = Gtk.ListStore(str)
        prev_store = Gtk.ListStore(str)
        [new_store.append([d]) for d in diffs if d.startswith("+")]
        [prev_store.append([d]) for d in diffs if d.startswith("-")]
        new_list.load_store(new_store)
        prev_list.load_store(prev_store)

    def __columns(self):
        merged_col = Gtk.TreeViewColumn("")
        left_renderer = Gtk.CellRendererText()

        merged_col.pack_start(left_renderer, True)

        merged_col.add_attribute(left_renderer, "text", 0)

        return [merged_col]
