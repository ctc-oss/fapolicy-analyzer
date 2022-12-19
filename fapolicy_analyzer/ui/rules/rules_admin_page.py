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
from typing import Any, Optional, Sequence, Tuple

from fapolicy_analyzer import Rule, System
from fapolicy_analyzer.ui.actions import (
    Notification,
    NotificationType,
    add_notification,
    apply_changesets,
    modify_rules_text,
    remove_notification,
    request_rules,
    request_rules_text,
)
from fapolicy_analyzer.ui.changeset_wrapper import Changeset, RuleChangeset
from fapolicy_analyzer.ui.rules.rules_list_view import RulesListView
from fapolicy_analyzer.ui.rules.rules_status_info import RulesStatusInfo
from fapolicy_analyzer.ui.rules.rules_text_view import RulesTextView
from fapolicy_analyzer.ui.store import (
    dispatch,
    get_notifications_feature,
    get_system_feature,
)
from fapolicy_analyzer.ui.strings import (
    APPLY_CHANGESETS_ERROR_MESSAGE,
    RULES_CHANGESET_PARSE_ERROR,
    RULES_LOAD_ERROR,
    RULES_TEXT_LOAD_ERROR,
    RULES_VALIDATION_ERROR,
    RULES_VALIDATION_WARNING,
)
from fapolicy_analyzer.ui.ui_page import UIAction, UIPage
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget

VALIDATION_NOTE_CATEGORY = "invalid rules"


class RulesAdminPage(UIConnectedWidget, UIPage):
    def __init__(self):
        UIConnectedWidget.__init__(
            self, get_system_feature(), on_next=self.on_next_system
        )

        self.__notification_subscription = get_notifications_feature().subscribe(
            on_next=self.on_next_notifications,
        )

        actions = {
            "rules": [
                UIAction(
                    name="Validate",
                    tooltip="Validate Rules",
                    icon="emblem-default",
                    signals={"clicked": self.on_validate_clicked},
                    sensitivity_func=self.__rules_unvalidated,
                ),
                UIAction(
                    name="Save",
                    tooltip="Save Rules",
                    icon="document-save",
                    signals={"clicked": self.on_save_clicked},
                    sensitivity_func=self.__rules_dirty,
                ),
            ],
        }
        UIPage.__init__(self, actions)

        self.__init_child_widgets()

        self.__rules: Sequence[Rule] = []
        self.__modified_rules_text: str = ""
        self.__rules_text: str = ""
        self.__rules_validated: bool = True
        self.__error_rules: Optional[str] = None
        self.__error_text: Optional[str] = None
        self.__loading_rules: bool = False
        self.__loading_text: bool = False
        self.__changesets: Sequence[Changeset] = []
        self.__saving: bool = False
        self.__system: System = None
        self.__validation_notifications: Sequence[Notification] = []

        self.__load_rules()

    def __init_child_widgets(self):
        self._text_view: RulesTextView = RulesTextView()
        self.get_object("editorViewContent").pack_start(
            self._text_view.get_ref(), True, True, 0
        )
        self._text_view.rules_changed += self.on_text_view_rules_changed

        self._list_view: RulesListView = RulesListView()
        self.get_object("rulesViewContent").pack_start(
            self._list_view.get_ref(), True, True, 0
        )

        self.__status_info = RulesStatusInfo()
        self.get_object("statusInfoContainer").add(self.__status_info.get_ref())

    def __load_rules(self):
        self.__loading_rules = True
        dispatch(request_rules())
        self.__loading_text = True
        dispatch(request_rules_text())

    def __rules_unvalidated(self) -> bool:
        return not self.__rules_validated

    def __rules_dirty(self) -> bool:
        is_dirty = (
            bool(self.__modified_rules_text)
            and self.__modified_rules_text != self.__rules_text
        )
        text = "*Rules Editor" if is_dirty else "Rules Editor"
        self.get_object("editorView").set_text(text)
        return is_dirty

    def __update_list_view(self, changeset: RuleChangeset):
        if self.__system:
            try:
                tmp_system = changeset.apply_to_system(self.__system)
                self._list_view.render_rules(tmp_system.rules())
            except Exception:
                logging.warning("Failed to parse validating changeset")

    def __clear_validation_notifications(self):
        for note in self.__validation_notifications:
            dispatch(remove_notification(note.id))

    def __build_and_validate_changeset(self) -> Tuple[RuleChangeset, bool]:
        changeset = RuleChangeset()
        valid = True

        try:
            changeset.parse(self.__modified_rules_text)
        except Exception as e:
            logging.error("Error setting changeset rules: %s", e)
            dispatch(
                add_notification(
                    RULES_CHANGESET_PARSE_ERROR,
                    NotificationType.ERROR,
                )
            )
            return changeset, False

        self.__rules_validated = True
        self.__clear_validation_notifications()
        rules = changeset.rules()

        if not all([r.is_valid for r in rules]):
            dispatch(
                add_notification(
                    RULES_VALIDATION_ERROR,
                    NotificationType.ERROR,
                    category=VALIDATION_NOTE_CATEGORY,
                )
            )
            valid = False

        if any([True for r in rules for i in r.info if i.category.lower() == "w"]):
            dispatch(
                add_notification(
                    RULES_VALIDATION_WARNING,
                    NotificationType.WARN,
                    category=VALIDATION_NOTE_CATEGORY,
                )
            )
        return changeset, valid

    def _dispose(self):
        UIConnectedWidget._dispose(self)
        if self.__notification_subscription:
            self.__notification_subscription.dispose()

    def on_save_clicked(self, *args):
        changeset, valid = self.__build_and_validate_changeset()
        self.__update_list_view(changeset)
        if valid:
            self.__saving = True
            dispatch(apply_changesets(changeset))
        else:
            self.__status_info.render_rule_status(changeset.rules())

    def on_validate_clicked(self, *args):
        changeset, _ = self.__build_and_validate_changeset()
        self.__update_list_view(changeset)
        self.__status_info.render_rule_status(changeset.rules())

        # dispatch to force toolbar refresh
        dispatch(modify_rules_text(self.__rules_validated))

    def on_text_view_rules_changed(self, rules: str):
        self.__modified_rules_text = rules
        self.__rules_validated = False
        dispatch(modify_rules_text(rules))

    def highlight_row_from_data(self, data: Any):
        self._list_view.highlight_row_from_data(data)

    def on_next_system(self, system: Any):
        changesetState = system.get("changesets")
        rules_state = system.get("rules")
        text_state = system.get("rules_text")
        system_state = system.get("system")

        if self.__system != system_state.system:
            self.__system = system_state.system

        if self.__saving and changesetState.error:
            self.__saving = False
            logging.error(
                "%s: %s", APPLY_CHANGESETS_ERROR_MESSAGE, changesetState.error
            )
            dispatch(
                add_notification(APPLY_CHANGESETS_ERROR_MESSAGE, NotificationType.ERROR)
            )

        elif self.__changesets != changesetState.changesets:
            self.__saving = False
            self.__changesets = changesetState.changesets
            self.__load_rules()

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
            self._list_view.render_rules(self.__rules)
            self.__status_info.render_rule_status(self.__rules)

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
            self._text_view.render_rules(self.__rules_text)
            self.__rules_validated = True

    def on_next_notifications(self, notifications: Sequence[Notification]):
        self.__validation_notifications = [
            n for n in notifications if n.category == VALIDATION_NOTE_CATEGORY
        ]
