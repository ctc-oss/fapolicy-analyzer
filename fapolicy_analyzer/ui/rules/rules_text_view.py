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


import os
from importlib import resources

import gi
from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget

gi.require_version("GtkSource", "3.0")
from gi.repository import GtkSource  # isort: skip


class RulesTextView(UIBuilderWidget):
    def __init__(self):
        super().__init__()
        self.__text_view = self.get_object("textView")

        buffer = GtkSource.Buffer.new_with_language(self.__get_view_lang())
        buffer.set_style_scheme(self.__get_view_style())
        self.__text_view.set_buffer(buffer)

    def __get_view_lang(self):
        lang_manager = GtkSource.LanguageManager.get_default()
        with resources.path(
            "fapolicy_analyzer.resources.sourceview.language-specs",
            "fapolicyd-rules.lang",
        ) as path:
            lang_manager.set_search_path(
                [
                    *lang_manager.get_search_path(),
                    os.path.dirname(path.as_posix()),
                ]
            )
        return lang_manager.get_language("fapolicyd-rules")

    def __get_view_style(self):
        style_manager = GtkSource.StyleSchemeManager.get_default()
        with resources.path(
            "fapolicy_analyzer.resources.sourceview.styles", "fapolicyd.xml"
        ) as path:
            style_manager.prepend_search_path(path.as_posix())
        return style_manager.get_scheme("fapolicyd")

    def render_rules(self, rules_text: str):
        buffer = self.__text_view.get_buffer()
        buffer.begin_not_undoable_action()
        buffer.set_text(rules_text)
        buffer.end_not_undoable_action()
