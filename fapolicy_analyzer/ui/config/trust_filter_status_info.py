# Copyright Concurrent Technologies Corporation 2024
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

import gi
from fapolicy_analyzer.ui.editor_status_info import EditorStatusInfo

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


class TrustFilterStatusInfo(EditorStatusInfo):
    def __init__(self):
        super().__init__()
        self._status_list.append_column(
            Gtk.TreeViewColumn(
                "",
                Gtk.CellRendererText(),
                text=0,
                foreground=1,
                weight=2,
            )
        )

        self._STATUS_HEADERS = {
            "e": _("invalid filters(s) found"),
            "w": _("warning(s) found"),
            "i": _("informational message(s)"),
        }

    def render_filter_status(self, info):
        stats = {"e": [], "w": [], "i": []}
        for i in info:
            stats.get(i.category, []).append(i.message)

        store = Gtk.TreeStore(str, str, int, bool)

        for cat, messages in stats.items():
            count = len(messages)
            style = self._status_text_style(count, cat)
            parent = store.append(
                None,
                [
                    f"{count} {self._STATUS_HEADERS[cat]}",
                    *style,
                    self.get_row_collapsed(cat),
                ],
            )
            for m in messages:
                store.append(parent, [m, *style, True])

        self._status_list.set_model(store)
        self._model = self._status_list.get_model()
        self.restore_row_collapse()
