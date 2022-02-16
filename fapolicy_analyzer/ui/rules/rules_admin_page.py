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
from typing import Any, Optional, Sequence

from fapolicy_analyzer import Rule
from fapolicy_analyzer.ui.actions import (
    NotificationType,
    add_notification,
    request_rules,
)
from fapolicy_analyzer.ui.rules.rules_list_view import RulesListView
from fapolicy_analyzer.ui.rules.rules_text_view import RulesTextView
from fapolicy_analyzer.ui.store import dispatch, get_system_feature
from fapolicy_analyzer.ui.strings import RULES_LOAD_ERROR
from fapolicy_analyzer.ui.ui_page import UIPage
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget


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
        self.__error: Optional[str] = None
        self.__loading: bool = False

        self.__load_rules()

    def __load_rules(self):
        self.__loading = True
        dispatch(request_rules())

    def __populate_rules(self):
        self.__text_view.render_rules(self.__rules)
        self.__list_view.render_rules(self.__rules)

    def on_next_system(self, system: Any):
        rules_state = system.get("rules")

        if not rules_state.loading and self.__error != rules_state.error:
            self.__error = rules_state.error
            self.__loading = False
            logging.error("%s: %s", RULES_LOAD_ERROR, self.__error)
            dispatch(add_notification(RULES_LOAD_ERROR, NotificationType.ERROR))
        elif (
            self.__loading
            and not rules_state.loading
            and self.__rules != rules_state.rules
        ):
            self.__error = None
            self.__loading = False
            self.__rules = rules_state.rules
            self.__populate_rules()
