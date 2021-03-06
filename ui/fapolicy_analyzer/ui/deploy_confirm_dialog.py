import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from threading import Thread
from time import sleep


class DeployConfirmDialog:
    def __init__(self, parent=None):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../glade/deploy_confirm_dialog.glade")
        self.builder.connect_signals(self)
        self.dialog = self.builder.get_object("deployConfirmDialog")
        if parent:
            self.dialog.set_transient_for(parent)

    def get_content(self):
        return self.dialog

    def on_after_show(self, *args):
        thread = Thread(target=self.reset_countdown)
        thread.daemon = True
        thread.start()

    def reset_countdown(self):
        for i in reversed(range(1, 16)):
            GLib.idle_add(
                self.dialog.format_secondary_text,
                f"Reverting to previous settings in {i} seconds",
            )
            sleep(1)
        GLib.idle_add(self.dialog.response, Gtk.ResponseType.NO)
