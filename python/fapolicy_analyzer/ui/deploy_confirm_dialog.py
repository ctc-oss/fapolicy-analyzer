import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from threading import Thread
from time import sleep
from locale import gettext as _
from .ui_widget import UIWidget
from fapolicy_analyzer.util.format import f


class DeployConfirmDialog(UIWidget):
    def __init__(self, parent=None, cancel_time=30):
        super().__init__()
        self.dialog = self.builder.get_object("deployConfirmDialog")
        if parent:
            self.dialog.set_transient_for(parent)
        self.cancel_time = cancel_time

    def get_content(self):
        return self.dialog

    def on_after_show(self, *args):
        thread = Thread(target=self.reset_countdown)
        thread.daemon = True
        thread.start()

    def reset_countdown(self):
        for i in reversed(range(0, self.cancel_time)):
            GLib.idle_add(
                self.dialog.format_secondary_text,
                f(_("Reverting to previous settings in {i+1} seconds")),
            )
            sleep(1)
        GLib.idle_add(self.dialog.response, Gtk.ResponseType.NO)
