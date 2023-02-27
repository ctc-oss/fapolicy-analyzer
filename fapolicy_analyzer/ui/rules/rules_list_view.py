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

from itertools import groupby
from typing import Any, Sequence, Tuple

import gi

from fapolicy_analyzer import Rule
from fapolicy_analyzer.ui.configs import Colors, FontWeights
from fapolicy_analyzer.ui.searchable_list import SearchableList
from fapolicy_analyzer.ui.strings import RULE_LABEL, RULES_LABEL

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango  # isort: skip


class RulesListView(SearchableList):
    def __init__(self):
        super().__init__(
            self.__columns(),
            view_headers_visible=False,
            defaultSortIndex=1,
        )

        self.treeView.get_selection().set_select_function(lambda *_: False)
        self.model = self.treeView.get_model()

    def __columns(self):
        merged_col = Gtk.TreeViewColumn("")
        left_renderer = Gtk.CellRendererText()
        right_renderer = Gtk.CellRendererText()

        merged_col.pack_start(left_renderer, False)
        merged_col.pack_start(right_renderer, True)

        merged_col.add_attribute(left_renderer, "text", 5)
        merged_col.add_attribute(left_renderer, "cell_background", 2)
        merged_col.add_attribute(left_renderer, "foreground", 3)
        merged_col.add_attribute(left_renderer, "weight", 4)

        merged_col.add_attribute(right_renderer, "text", 0)
        merged_col.add_attribute(right_renderer, "cell_background", 2)
        merged_col.add_attribute(right_renderer, "foreground", 3)
        merged_col.add_attribute(right_renderer, "weight", 4)
        merged_col.add_attribute(right_renderer, "style", 6)

        return [merged_col]

    def __rule_text_style(self, rule: Rule) -> Tuple[str, int]:
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

    def __append_origin(self, store, origin):
        return store.append(
            None,
            [
                f"[{origin}]",
                -1,
                Colors.WHITE,
                Colors.DARK_GRAY,
                FontWeights.BOLD,
                "",
                Pango.Style.ITALIC,
                self.get_collapsed_status(store, None),
            ],
        )

    def __append_rule(self, store, rule, parent):
        row_color = (
            Colors.WHITE
        )  # Colors.SHADED if store.iter_n_children(parent) % 2 else Colors.WHITE
        return store.append(
            parent,
            [
                rule.text,
                rule.id,
                row_color,
                *self.__rule_text_style(rule),
                str(rule.id),
                Pango.Style.NORMAL,
                self.get_collapsed_status(store, parent),
            ],
        )

    def __append_info(self, store, rule, info, parent_row):
        return store.append(
            parent_row,
            [
                f"[{info.category}] {info.message}",
                rule.id,
                store.get_value(parent_row, 2),  # parent row color
                self.__info_cat_text_color(info.category),
                FontWeights.NORMAL,
                "",
                Pango.Style.NORMAL,
                self.get_collapsed_status(store, parent_row),
            ],
        )

    def get_collapsed_status(self, store, parent):
        model = self.treeView.get_model()
        is_collapsed = None
        if store:
            if parent is None:
                return True
            is_collapsed = next(iter(store.get(parent, 7)))
            return is_collapsed
        else:
            return False

    def get_child_model_from_sort(self, view, iter):
        sort_model = view.get_model()
        filter_iter = sort_model.convert_iter_to_child_iter(iter)
        filter_model = sort_model.get_model()
        model_iter = filter_model.convert_iter_to_child_iter(filter_iter)
        self.model = filter_model.get_model()
        return model_iter

    def on_row_collapsed(self, view, iter, path):
        model_iter = self.get_child_model_from_sort(view, iter)
        self.model.set(model_iter, 7, True)
 
    def on_row_expanded(self, view, iter, path):
        model_iter = self.get_child_model_from_sort(view, iter)
        self.model.set(model_iter, 7, False)

    def restore_row_collapse(self):
        def toggle_collapse(store, treepath, treeiter):
            self.treeView.collapse_row(treepath) if store[treeiter][7] else self.treeView.expand_row(treepath, False)
        if not self.model is None:
            self.model.foreach(toggle_collapse)

    def highlight_row_from_data(self, data: Any):
        row = self.find_selected_row_by_data(data, 1)
        if row:
            selection = self.treeView.get_selection()
            selection.set_select_function(
                lambda *_: True if _[2] == row else False, row
            )
            selection.select_path(row)
            self.treeView.scroll_to_cell(row, use_align=True, row_align=0.0)

    def __expand_rows_at_root(self, store):
        iter = store.get_iter_first()
        while iter:
            self.treeView.expand_row(store.get_path(iter), False)
            iter = store.iter_next(iter)

    def _update_list_status(self, count):
        label = RULE_LABEL if count == 1 else RULES_LABEL
        self.treeCount.set_text(" ".join([str(count), label]))

    def render_rules(self, rules: Sequence[Rule]):
        store = Gtk.TreeStore(str, int, str, str, int, str, Pango.Style, bool)
        rule_map = {o: list(r) for o, r in groupby(rules or [], lambda r: r.origin)}

        for origin in rule_map.keys():
            origin_row = self.__append_origin(store, origin)
            for rule in rule_map[origin]:
                rule_row = self.__append_rule(store, rule, origin_row)
                if rule.info:
                    for info in rule.info:
                        self.__append_info(store, rule, info, rule_row)

        self.load_store(store)
        #self.__expand_rows_at_root(store)
        self.restore_row_collapse()
