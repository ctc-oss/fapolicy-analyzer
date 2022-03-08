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

from fapolicy_analyzer.ui.actions import NotificationType, add_notification
from fapolicy_analyzer.ui.store import dispatch
from fapolicy_analyzer.ui.strings import RULES_FILE_READ_ERROR
from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget


class RulesTextView(UIBuilderWidget):
    def __init__(self):
        super().__init__()
        self.__text_view = self.get_object("textView")
        self.__text_view.set_show_line_numbers(True)

    def render_rules(self, rules_path: str):
        text = ""
        try:
            with open(rules_path, "r") as f:
                text = f.read()
        except (IOError, FileNotFoundError) as e:
            logging.error("%s: %s", RULES_FILE_READ_ERROR, e)
            dispatch(add_notification(RULES_FILE_READ_ERROR, NotificationType.ERROR))

        self.__text_view.get_buffer().set_text(text)
