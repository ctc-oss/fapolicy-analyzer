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
from typing import Any

from fapolicy_analyzer.ui.config_text_view import ConfigTextView
from fapolicy_analyzer.ui.config_status_info import ConfigStatusInfo
from fapolicy_analyzer.ui.ui_page import UIAction, UIPage
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget

# from fapolicy_analyzer.ui.actions import ()
from fapolicy_analyzer.ui.store import (
    dispatch,
    get_system_feature,
)


class ConfigAdminPage(UIConnectedWidget):
    def __init__(self):
        UIConnectedWidget.__init__(
            self, get_system_feature(), on_next=self.on_next_system
        )
        actions = {}
        UIPage.__init__(self, actions)

        self.__modified_config_text: str = ""
        self.__config_validated: bool = True
        self.__init_child_widgets()
        self._text_view.config_changed += self.on_text_view_config_changed

    def __init_child_widgets(self):
        self._text_view: ConfigTextView = ConfigTextView()
        self.get_object("configContentArea").pack_start(
            self._text_view.get_ref(), True, True, 0
        )
        self._text_view.config_changed += self.on_text_view_config_changed

        self.__status_info = ConfigStatusInfo()
        self.get_object("configStatusFrame").add(self.__status_info.get_ref())

    def on_next_system(self, system: Any):
        system_state = system.get("system")

    def on_text_view_config_changed(self, config: str):
        self.__modified_config_text = config
        self.__config_validated = False
        # dispatch(modify_config_text(config))
