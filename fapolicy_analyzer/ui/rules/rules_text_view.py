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
from typing import Optional

from fapolicy_analyzer.ui.editable_text_view import EditableTextView


class RulesTextView(EditableTextView):
    def __init__(self):
        self.__events__ = ["rules_changed"]
        super().__init__()

        self._buffer.connect("changed", self.on_rules_changed)

    def on_rules_changed(self, buffer):
        self.rules_changed(self._get_text())

    def _get_view_lang_id(self) -> Optional[str]:
        return "fapolicyd-rules.lang"
