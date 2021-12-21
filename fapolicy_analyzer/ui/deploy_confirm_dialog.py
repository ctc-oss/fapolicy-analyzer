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

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from threading import Thread
from time import sleep
from locale import gettext as _
from .ui_widget import UIBuilderWidget
from fapolicy_analyzer.util.format import f


class DeployConfirmDialog(UIBuilderWidget):
    def __init__(self, parent=None, cancel_time=30):
        super().__init__()
        if parent:
            self.get_ref().set_transient_for(parent)
        self.cancel_time = cancel_time

    def on_after_show(self, *args):
        thread = Thread(target=self.reset_countdown)
        thread.daemon = True
        thread.start()

    def reset_countdown(self):
        dialog = self.get_ref()
        for i in reversed(range(0, self.cancel_time)):
            GLib.idle_add(
                dialog.format_secondary_text,
                f(_("Reverting to previous settings in {i+1} seconds")),
            )
            sleep(1)
        GLib.idle_add(dialog.response, Gtk.ResponseType.NO)
