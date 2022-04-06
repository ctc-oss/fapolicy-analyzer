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
from locale import gettext as _
from typing import Any, Optional, Sequence

from fapolicy_analyzer import Rule
from fapolicy_analyzer.ui.actions import (
    NotificationType,
    add_notification,
    request_rules,
    request_rules_text,
)
from fapolicy_analyzer.ui.rules.rules_list_view import RulesListView
from fapolicy_analyzer.ui.rules.rules_text_view import RulesTextView
from fapolicy_analyzer.ui.store import dispatch, get_system_feature
from fapolicy_analyzer.ui.strings import RULES_LOAD_ERROR, RULES_TEXT_LOAD_ERROR
from fapolicy_analyzer.ui.ui_page import UIPage
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget
from fapolicy_analyzer.util.format import f


class RulesAdminPage(UIConnectedWidget, UIPage):
    def __init__(self):
        UIConnectedWidget.__init__(
            self, get_system_feature(), on_next=self.on_next_system
        )
        UIPage.__init__(self, {})

        self.__text_view: RulesTextView = RulesTextView()
        self.get_object("textEditorContent").pack_start(
            self.__text_view.get_ref(), True, True, 0
        )

        self.__list_view: RulesListView = RulesListView()
        self.get_object("guidedEditorContent").pack_start(
            self.__list_view.get_ref(), True, True, 0
        )

        self.__rules: Sequence[Rule] = []
        self.__rules_text: str = ""
        self.__error_rules: Optional[str] = None
        self.__error_text: Optional[str] = None
        self.__loading_rules: bool = False
        self.__loading_text: bool = False

        self.__load_rules()

    def __load_rules(self):
        self.__loading_rules = True
        dispatch(request_rules())
        self.__loading_text = True
        dispatch(request_rules_text())

    def __render_rule_status(self):
        view = self.get_object("statusInfo")
        categories = [i.category for r in self.__rules for i in r.info]
        invalid_count = sum(not r.is_valid for r in self.__rules)  # noqa: F841
        warning_count = sum(c == "w" for c in categories)  # noqa: F841
        info_count = sum(c == "i" for c in categories)  # noqa: F841
        view.get_buffer().set_text(
            f(
                _(
                    """{invalid_count} invalid rule found
{warning_count} warning(s) found
{info_count} informational message(s)"""
                )
            )
        )

    def on_next_system(self, system: Any):
        rules_state = system.get("rules")
        text_state = system.get("rules_text")

        if not rules_state.loading and self.__error_rules != rules_state.error:
            self.__error_rules = rules_state.error
            self.__loading_rules = False
            logging.error("%s: %s", RULES_LOAD_ERROR, self.__error_rules)
            dispatch(add_notification(RULES_LOAD_ERROR, NotificationType.ERROR))
        elif (
            self.__loading_rules
            and not rules_state.loading
            and self.__rules != rules_state.rules
        ):
            self.__error_rules = None
            self.__loading_rules = False
            self.__rules = rules_state.rules
            self.__list_view.render_rules(self.__rules)
            self.__render_rule_status()

        if not text_state.loading and self.__error_text != text_state.error:
            self.__error_text = text_state.error
            self.__loading_text = False
            logging.error("%s: %s", RULES_TEXT_LOAD_ERROR, self.__error_text)
            dispatch(add_notification(RULES_TEXT_LOAD_ERROR, NotificationType.ERROR))
        elif (
            self.__loading_text
            and not text_state.loading
            and self.__rules_text != text_state.rules_text
        ):
            self.__error_text = None
            self.__loading_text = False
            self.__rules_text = text_state.rules_text
            self.__text_view.render_rules(self.__rules_text)
