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
from fapolicy_analyzer.ui.configs import Colors, FontWeights
from fapolicy_analyzer.ui.searchable_list import SearchableList
from fapolicy_analyzer.ui.strings import RULE_LABEL, RULES_LABEL

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


class RulesListView(SearchableList):
    def __init__(self):
        super().__init__(
            self.__columns(),
            view_headers_visible=False,
            defaultSortIndex=1,
        )

        self.treeView.get_selection().set_select_function(lambda *_: False)

    def __columns(self):
        return [
            Gtk.TreeViewColumn(
                "",
                Gtk.CellRendererText(),
                text=0,
                cell_background=2,
                foreground=3,
                weight=4,
            )
        ]

    def __rule_text_style(self, rule: Rule) -> tuple[str, int]:
        info_cats = [i.category for i in rule.info]
        return (
            (Colors.RED, FontWeights.BOLD)
            if not rule.is_valid
            else (Colors.ORANGE, FontWeights.BOLD)
            if "w" in info_cats
            else (Colors.BLUE, FontWeights.BOLD)
            if "i" in info_cats
            else (Colors.BLACK, FontWeights.NORMAL)
        )

    def __info_cat_text_color(self, cat: str) -> str:
        color_map = {"e": Colors.RED, "w": Colors.ORANGE, "i": Colors.BLUE}
        return color_map.get(cat, Colors.BLACK)

    def _update_tree_count(self, count):
        label = RULE_LABEL if count == 1 else RULES_LABEL
        self.treeCount.set_text(" ".join([str(count), label]))

    def render_rules(self, rules: Sequence[Rule]):
        store = Gtk.TreeStore(str, int, str, str, int)

        for idx, rule in enumerate(rules):
            row_color = Colors.WHITE if idx % 2 else Colors.SHADED
            text_style = self.__rule_text_style(rule)
            parent = store.append(
                None, [str(rule.id) + " " + rule.text, rule.id, row_color, text_style[0], text_style[1]]
            )
            if rule.info:
                for info in rule.info:
                    store.append(
                        parent,
                        [
                            f"[{info.category}] {info.message}",
                            rule.id,
                            row_color,
                            self.__info_cat_text_color(info.category),
                            FontWeights.NORMAL,
                        ],
                    )

        self.load_store(store)
