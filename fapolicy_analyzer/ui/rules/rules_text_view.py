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


import logging
import os

import gi

try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources

from events import Events
from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget

gi.require_version("GtkSource", "3.0")
from gi.repository import GtkSource  # isort: skip


class RulesTextView(UIBuilderWidget, Events):
    __events__ = ["rules_changed"]

    def __init__(self):
        UIBuilderWidget.__init__(self)
        Events.__init__(self)
        self.__text_view = self.get_object("textView")

        self.__buffer = GtkSource.Buffer()
        language = self.__get_view_lang()
        if language:
            self.__buffer.set_language(language)
        style = self.__get_view_style()
        if style:
            self.__buffer.set_style_scheme(self.__get_view_style())
        self.__buffer.connect("changed", self.on_rules_changed)
        self.__text_view.set_buffer(self.__buffer)

    def __get_view_lang(self):
        lang_manager = GtkSource.LanguageManager.get_default()
        try:
            with resources.path(
                "fapolicy_analyzer.resources.sourceview.language-specs",
                "fapolicyd-rules.lang",
            ) as path:
                if (
                    os.path.dirname(path.as_posix())
                    not in lang_manager.get_search_path()
                ):
                    lang_manager.set_search_path(
                        [
                            *lang_manager.get_search_path(),
                            os.path.dirname(path.as_posix()),
                        ]
                    )
        except Exception as ex:
            logging.warning("Could not load the rules language file")
            logging.debug(
                "Error loading GtkSource language file fapolicyd-rules.lang", ex
            )

        return lang_manager.get_language("fapolicyd-rules")

    def __get_view_style(self):
        style_manager = GtkSource.StyleSchemeManager.get_default()
        try:
            with resources.path(
                "fapolicy_analyzer.resources.sourceview.styles", "fapolicyd.xml"
            ) as path:
                style_manager.prepend_search_path(path.as_posix())
        except Exception as ex:
            logging.warning("Could not load the rules style file")
            logging.debug("Error loading GtkSource style file fapolicyd.xml", ex)

        return style_manager.get_scheme("fapolicyd")

    def __get_text(self):
        return self.__buffer.get_text(
            self.__buffer.get_start_iter(), self.__buffer.get_end_iter(), True
        )

    def render_rules(self, rules_text: str):
        self.__buffer.begin_not_undoable_action()
        self.__buffer.set_text(rules_text)
        self.__buffer.end_not_undoable_action()

    # def get_rules(self) -> str:
    #     return self.__get_text()

    def on_rules_changed(self, buffer):
        self.rules_changed(self.__get_text())
