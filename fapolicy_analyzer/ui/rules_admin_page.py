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

from typing import Any

from fapolicy_analyzer.ui.store import get_system_feature
from fapolicy_analyzer.ui.ui_page import UIPage
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget


class RulesAdminPage(UIConnectedWidget, UIPage):
    def __init__(self):
        UIConnectedWidget.__init__(
            self, get_system_feature(), on_next=self.on_next_system
        )
        UIPage.__init__(self, {})

    def on_next_system(self, system: Any):
        pass
