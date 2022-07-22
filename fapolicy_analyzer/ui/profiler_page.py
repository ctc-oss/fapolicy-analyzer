# Copyright Concurrent Technologies Corporation 2021
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
from fapolicy_analyzer.ui.ui_page import UIAction, UIPage
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget
from .store import dispatch, get_system_feature

from .configs import Sizing
from fapolicy_analyzer.util.format import f

class ProfilerPage(UIConnectedWidget, UIPage):
    def __init__(self):
        UIConnectedWidget.__init__(self, get_system_feature())

        actions = {
            "start": [
                UIAction(
                    "Start",
                    "Start Test",
                    "media-playback-start",
                    {"clicked": self.on_test_activate},
                    sensitivity_func=self.start_button_sensitivity
                )
            ],
            "stop": [
                UIAction(
                    "Stop",
                    "Stop Test",
                    "media-playback-stop",
                    {},
                    sensitivity_func=self.stop_button_sensitivity
                )
            ]
        }

        UIPage.__init__(self, actions)

        self._fapd_mgr = None
        self._fapd_profiler = None
        self.running = False

    def stop_button_sensitivity(self):
        return self.running

    def start_button_sensitivity(self):
        return not self.running

    def get_text(self):
        entryDict = {
            "executeText": self.get_object("executeEntry").get_text(),
            "argText": self.get_object("argEntry").get_text(),
            "userText": self.get_object("userEntry").get_text(),
            "dirText": self.get_object("dirEntry").get_text(),
            "envText": self.get_object("envEntry").get_text(),
        }

    def on_test_activate(self, *args):
        profiling_args = self.get_text()
        logging.debug(f"Entry text = {profiling_args}")
        self.running = True
        self._fapd_profiler.start_prof_session(profiling_args)
        fapd_prof_stderr = self._fapd_profiler.fapd_prof_stderr
        logging.debug(f"Started prof session, stderr={fapd_prof_stderr}")

        sleep(4)
        self._fapd_profiler.stop_prof_session()
        self.running = False
