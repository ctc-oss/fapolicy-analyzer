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

import sys

import fapolicy_analyzer.ui.strings as strings
import gi
from fapolicy_analyzer.ui.main_window import MainWindow
from fapolicy_analyzer.ui.store import get_system_feature
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk  # isort: skip


def trust_db_access_failure_dlg():
    """
    Presents a modal dialog alerting the user that Trust database read
    access failed.
    """

    dlgSessionRestorePrompt = Gtk.Dialog(
        title=strings.TRUST_DB_READ_FAILURE_DIALOG_TITLE
    )
    dlgSessionRestorePrompt.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)

    label = Gtk.Label(label=strings.TRUST_DB_READ_FAILURE_DIALOG_TEXT)
    hbox = dlgSessionRestorePrompt.get_content_area()
    label.set_justify(Gtk.Justification.CENTER)
    hbox.add(label)
    dlgSessionRestorePrompt.show_all()
    dlgSessionRestorePrompt.run()
    dlgSessionRestorePrompt.destroy()


class SplashScreen(UIConnectedWidget):
    def __init__(self):
        super().__init__(get_system_feature(), on_next=self.on_next_system)
        self.progressBar = self.get_object("progressBar")
        self.window = self.get_ref()
        self.window.show_all()
        self.timeout_id = GLib.timeout_add(100, self.on_timeout, None)
        self.progressBar.pulse()

    def on_next_system(self, system):
        system_state = system.get("system")

        if system_state.error:
            self.dispose()
            trust_db_access_failure_dlg()
            sys.exit(1)

        if system_state.system:
            self.dispose()
            MainWindow()

    def on_timeout(self, *args):
        self.progressBar.pulse()
        return True
