import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .ui_widget import UIWidget


class ConfirmDialog(UIWidget):
    def __init__(self, text, secondary_text=None, parent=None):
        self.dialog = Gtk.MessageDialog(
            transient_for=parent if parent else None,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=text,
        )

        if secondary_text:
            self.dialog.format_secondary_text(secondary_text)

        self.dialog.get_widget_for_response(Gtk.ResponseType.NO).grab_focus()

    def get_content(self):
        return self.dialog
