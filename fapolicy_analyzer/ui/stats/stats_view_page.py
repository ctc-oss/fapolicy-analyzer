# Copyright Concurrent Technologies Corporation 2024
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
from events import Events


from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget

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
from fapolicy_analyzer.ui.rules.rules_admin_page import VALIDATION_NOTE_CATEGORY
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


import numpy as np

from matplotlib.backends.backend_gtk3agg import \
    FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.figure import Figure


gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


class StatsViewPage(UIConnectedWidget, UIPage, Events):
    def __init__(self):
        features = [
            {get_system_feature(): {"on_next": self.on_next_system}},
        ]
        UIConnectedWidget.__init__(self, features=features)
        self.__events__ = [ "foo" ]
        Events.__init__(self)
        actions = {
            "stats": [],
        }
        UIPage.__init__(self, actions)

        self.__init_child_widgets()

    def __init_child_widgets(self):
        self.__text_view: GtkTextView = self.get_object("profilerOutput")
        print(self.__text_view)


    def on_next_system(self, system: Any):
        system_state = system.get("system")
