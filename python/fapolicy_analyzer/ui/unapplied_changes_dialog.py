import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from time import sleep
from .ui_widget import UIWidget


class UnappliedChangesDialog(UIWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.dialog = self.builder.get_object("unappliedChangesDialog")
        if parent:
            self.dialog.set_transient_for(parent)

    def get_content(self):
        return self.dialog
