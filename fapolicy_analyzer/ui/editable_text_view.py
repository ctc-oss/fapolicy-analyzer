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
from abc import abstractmethod
from typing import Optional

import gi

try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources

from fapolicy_analyzer.events import Events
from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget

gi.require_version("GtkSource", "3.0")
from gi.repository import GtkSource  # isort: skip


class EditableTextView(UIBuilderWidget, Events):
    def __init__(self):
        UIBuilderWidget.__init__(self, "editable_text_view")
        Events.__init__(self)
        self._text_view = self.get_object("textView")

        self._buffer = GtkSource.Buffer()
        language = self._get_view_lang()
        if language:
            self._buffer.set_language(language)
        style = self._get_view_style()
        if style:
            self._buffer.set_style_scheme(self._get_view_style())
        # self.__buffer.connect("changed", self.on_rules_changed)
        self._text_view.set_buffer(self._buffer)

    @abstractmethod
    def _get_view_lang_id(self) -> Optional[str]:
        pass

    def _get_view_lang(self):
        lang_id = self._get_view_lang_id()
        if lang_id:
            lang_manager = GtkSource.LanguageManager.get_default()
            try:
                with resources.path(
                    "fapolicy_analyzer.resources.sourceview.language-specs",
                    f"{lang_id}.lang",
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
                logging.debug(f"Error loading GtkSource language: {lang_id}", ex)

            return lang_manager.get_language(lang_id)

    def _get_view_style(self):
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

    def _get_text(self):
        return self._buffer.get_text(
            self._buffer.get_start_iter(), self._buffer.get_end_iter(), True
        )

    def render_text(self, text: str):
        self._buffer.begin_not_undoable_action()
        self._buffer.set_text(text)
        self._buffer.end_not_undoable_action()
