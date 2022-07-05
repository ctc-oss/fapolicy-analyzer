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

from locale import gettext as _
from typing import Tuple

import gi
from fapolicy_analyzer.ui.configs import Colors, FontWeights
from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip

_STATUS_HEADERS = {
    "e": _("invalid rule(s) found"),
    "w": _("warning(s) found"),
    "i": _("informational message(s)"),
}


class RulesStatusInfo(UIBuilderWidget):
    def __init__(self):
        super().__init__()
        self.__status_list = self.get_object("statusList")
        self.__status_list.get_selection().set_mode(Gtk.SelectionMode.NONE)
        self.__status_list.append_column(
            Gtk.TreeViewColumn(
                "",
                Gtk.CellRendererText(),
                text=0,
                foreground=1,
                weight=2,
            )
        )

    def __status_text_style(self, count: int, category: str) -> Tuple[str, int]:
        return (
            (Colors.BLACK, FontWeights.NORMAL)
            if not count
            else (Colors.RED, FontWeights.BOLD)
            if category.lower() == "e"
            else (Colors.ORANGE, FontWeights.BOLD)
            if category.lower() == "w"
            else (Colors.BLUE, FontWeights.BOLD)
            if category.lower() == "i"
            else (Colors.BLACK, FontWeights.NORMAL)
        )

    def render_rule_status(self, rules):
        stats = {"e": [], "w": [], "i": []}
        for r in rules:
            for i in r.info:
                stats.get(i.category, []).append(f"rule {r.id}: {i.message}")

        store = Gtk.TreeStore(str, str, int)

        for cat, messages in stats.items():
            count = len(messages)
            style = self.__status_text_style(count, cat)
            parent = store.append(None, [f"{count} {_STATUS_HEADERS[cat]}", *style])
            for m in messages:
                store.append(parent, [m, *style])

        self.__status_list.set_model(store)
