# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
#
#
# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib
from .main_window import MainWindow
from .store import get_system_feature
from .ui_widget import UIConnectedWidget


class SplashScreen(UIConnectedWidget):
    def __init__(self):
        super().__init__(get_system_feature(), on_next=self.on_next_system)
        self.progressBar = self.get_object("progressBar")
        self.window = self.get_ref()
        self.window.show_all()
        self.timeout_id = GLib.timeout_add(100, self.on_timeout, None)
        self.progressBar.pulse()

    def on_next_system(self, system):
        if system.get("initialized", False):
            self.dispose()
            MainWindow()

    def on_timeout(self, *args):
        self.progressBar.pulse()
        return True
