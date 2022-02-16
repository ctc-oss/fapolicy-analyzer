# Copyright Concurrent Technologies Corporation 2022
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

from typing import Sequence

import gi
from fapolicy_analyzer import Rule
from fapolicy_analyzer.ui.searchable_list import SearchableList

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


class RulesListView(SearchableList):
    def __init__(self):
        super().__init__(self.__columns(), view_headers_visible=False)

    def __columns(self):
        return [
            Gtk.TreeViewColumn("", Gtk.CellRendererText(), text=0, cell_background=2)
        ]

    def render_rules(self, rules: Sequence[Rule]):
        store = Gtk.ListStore(str, int, str)

        for idx, rule in enumerate(rules):
            row_color = "white" if idx % 2 else "gainsboro"
            store.append([rule.text, rule.id, row_color])

        self.load_store(store)
