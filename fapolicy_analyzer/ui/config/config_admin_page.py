# Copyright Concurrent Technologies Corporation 2023
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

import gi
import logging


from typing import Any, Optional, Sequence, Tuple
from fapolicy_analyzer.ui.actions import (
    NotificationType,
    add_notification,
    apply_changesets,
    modify_config_text,
    request_config_text,
)
from fapolicy_analyzer.ui.changeset_wrapper import Changeset, ConfigChangeset
from fapolicy_analyzer.ui.config.config_text_view import ConfigTextView
from fapolicy_analyzer.ui.config.config_status_info import ConfigStatusInfo
from fapolicy_analyzer.ui.strings import (
    APPLY_CHANGESETS_ERROR_MESSAGE,
    CONFIG_CHANGESET_PARSE_ERROR,
    CONFIG_TEXT_LOAD_ERROR,
    RULES_OVERRIDE_MESSAGE,
)
from fapolicy_analyzer.ui.ui_page import UIPage, UIAction
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget

# from fapolicy_analyzer.ui.actions import ()
from fapolicy_analyzer.ui.store import (
    dispatch,
    get_system_feature,
)

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


class ConfigAdminPage(UIConnectedWidget):
    def __init__(self):
        features = [
            {get_system_feature(): {"on_next": self.on_next_system}},
        ]
        UIConnectedWidget.__init__(self, features=features)
        actions = {
            "config": [
                UIAction(
                    name="Save",
                    tooltip="Save Config",
                    icon="document-save",
                    signals={"clicked": self.on_save_clicked},
                    sensitivity_func=self.__config_dirty,
                ),
            ],
        }
        UIPage.__init__(self, actions)
        self.__loading_text: bool = False
        self.__config_text: str = ""
        self.__changesets: Sequence[Changeset] = []
        self.__modified_config_text: str = ""
        self.__config_validated: bool = True
        self.__init_child_widgets()
        self.__error_text: Optional[str] = None
        self.__error_config: Optional[str] = None
        self.__saving: bool = False
        self._unsaved_changes = False
        self._first_pass = True

    def __init_child_widgets(self):
        self._text_view: ConfigTextView = ConfigTextView()
        self.get_object("configContentArea").pack_start(
            self._text_view.get_ref(), True, True, 0
        )
        self._text_view.config_changed += self.on_text_view_config_changed

        self.__status_info = ConfigStatusInfo()
        self.get_object("configStatusFrame").add(self.__status_info.get_ref())

        self.__load_config()

    def __load_config(self):
        self.__loading_text = True
        dispatch(request_config_text())

    def on_save_clicked(self, *args):
        changeset, valid = self.__build_and_validate_changeset(show_notifications=False)
        if valid:
            self.__saving = True
            dispatch(apply_changesets(changeset))
            self._unsaved_changes = False
        else:
            overrideDialog = self.get_object("saveOverrideDialog")
            self.get_object("overrideText").set_text(RULES_OVERRIDE_MESSAGE)
            resp = overrideDialog.run()
            if resp == Gtk.ResponseType.OK:
                self.__saving = True
                dispatch(apply_changesets(changeset))
                self._unsaved_changes = False
            else:
                self.__status_info.render_config_status(changeset.info())
            overrideDialog.hide()

    def __config_dirty(self) -> bool:
        return (
            bool(self.__modified_config_text)
            and self.__modified_config_text != self.__config_text
        )

    def __build_and_validate_changeset(
        self, show_notifications=True
    ) -> Tuple[ConfigChangeset, bool]:
        changeset = ConfigChangeset()
        valid = False

        try:
            changeset.parse(self.__modified_config_text)
            valid = changeset.is_valid()
        except Exception as e:
            logging.error("Error setting changeset config: %s", e)
            dispatch(
                add_notification(
                    CONFIG_CHANGESET_PARSE_ERROR,
                    NotificationType.ERROR,
                )
            )
            return changeset, valid

        self.__config_validated = valid
        # self.__clear_validation_notifications()

        return changeset, valid

    def on_next_system(self, system: Any):
        changesetState = system.get("changesets")
        text_state = system.get("config_text")
        system_state = system.get("system")

        if self.__saving and changesetState.error:
            self.__saving = False
            logging.error(
                "%s: %s", APPLY_CHANGESETS_ERROR_MESSAGE, changesetState.error
            )
            dispatch(
                add_notification(APPLY_CHANGESETS_ERROR_MESSAGE, NotificationType.ERROR)
            )
        elif self.__changesets != changesetState.changesets:
            self.__changesets = changesetState.changesets
            self.__config_text = ""
            self.__load_config()

        if not text_state.loading and self.__error_text != text_state.error:
            self.__error_text = text_state.error
            self.__loading_text = False
            logging.error("%s: %s", CONFIG_TEXT_LOAD_ERROR, self.__error_text)
            dispatch(add_notification(CONFIG_TEXT_LOAD_ERROR, NotificationType.ERROR))
        elif (
            self.__loading_text
            and not text_state.loading
            and self.__config_text != text_state.config_text
        ):

            self.__loading_text = False
            self.__config_text = text_state.config_text
            self._text_view.render_text(self.__config_text)
            self.__config_validated = True
            self.__status_info.render_config_status(system_state.system.config_info())

    def on_text_view_config_changed(self, config: str):
        self.__modified_config_text = config
        self.__config_validated = False
        # print(self._unsaved_changes, self._first_pass)
        self._unsaved_changes = True if not self._first_pass else False
        if self._first_pass:
            self._first_pass = False
        dispatch(modify_config_text(config))
