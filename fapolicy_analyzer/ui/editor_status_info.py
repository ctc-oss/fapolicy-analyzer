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

from typing import Tuple

import gi
from fapolicy_analyzer.ui.configs import Colors, FontWeights
from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


class EditorStatusInfo(UIBuilderWidget):
    def __init__(self):
        UIBuilderWidget.__init__(self, "editor_status_info")
        self._status_list = self.get_object("statusList")
        self._status_list.get_selection().set_mode(Gtk.SelectionMode.NONE)
        self._model = None

    def _status_text_style(self, count: int, category: str) -> Tuple[str, int]:
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

    def on_row_collapsed(self, view, iter, path):
        self._model.set(iter, 3, True)

    def on_row_expanded(self, view, iter, path):
        self._model.set(iter, 3, False)

    def get_row_collapsed(self, cat):
        if self._model is None:
            return True
        iter = self._model.get_iter_first()
        while iter:
            if self._STATUS_HEADERS[cat] in self._model[iter][0]:
                return self._model[iter][3]
            iter = self._model.iter_next(iter)

    def restore_row_collapse(self):
        def toggle_collapse(store, path, treeiter):
            self._status_list.collapse_row(path) if store[treeiter][
                3
            ] else self._status_list.expand_row(path, False)

        if self._model is not None:
            self._model.foreach(toggle_collapse)
