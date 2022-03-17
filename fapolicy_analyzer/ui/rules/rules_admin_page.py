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
from typing import Any, Mapping, Optional, Sequence

from fapolicy_analyzer import Rule
from fapolicy_analyzer.ui.actions import (NotificationType, add_notification,
                                          request_rules, request_rules_config)
from fapolicy_analyzer.ui.rules.rules_list_view import RulesListView
from fapolicy_analyzer.ui.rules.rules_text_view import RulesTextView
from fapolicy_analyzer.ui.store import dispatch, get_system_feature
from fapolicy_analyzer.ui.strings import (RULES_CONFIG_LOAD_ERROR,
                                          RULES_LOAD_ERROR)
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
        self.__rules_config: Mapping[str, str] = {}
        self.__error_rules: Optional[str] = None
        self.__error_config: Optional[str] = None
        self.__loading_rules: bool = False
        self.__loading_config: bool = False

        self.__load_rules()

    def __load_rules(self):
        self.__loading_rules = True
        dispatch(request_rules())
        self.__loading_config = True
        dispatch(request_rules_config())

    def on_next_system(self, system: Any):
        rules_state = system.get("rules")
        config_state = system.get("rules_config")

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

        if not config_state.loading and self.__error_config != config_state.error:
            self.__error_config = config_state.error
            self.__loading_config = False
            logging.error("%s: %s", RULES_CONFIG_LOAD_ERROR, self.__error_config)
            dispatch(add_notification(RULES_CONFIG_LOAD_ERROR, NotificationType.ERROR))
        elif (
            self.__loading_config
            and not config_state.loading
            and self.__rules_config != config_state.rules_config
        ):
            self.__error_config = None
            self.__loading_config = False
            self.__rules_config = config_state.rules_config
            self.__text_view.render_rules(self.__rules_config.get("rules_path"))
