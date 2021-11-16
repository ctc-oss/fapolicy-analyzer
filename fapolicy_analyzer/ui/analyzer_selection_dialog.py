import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from enum import Enum
from os import path
from .strings import OPEN_FILE_LABEL
from .ui_widget import UIBuilderWidget


class ANALYZER_SELECTION(Enum):
    TRUST_DATABASE_ADMIN = 0
    SCAN_SYSTEM = 1
    ANALYZE_FROM_AUDIT = 2


class AnalyzerSelectionDialog(UIBuilderWidget):
    def __init__(self, parent=None):
        super().__init__()
        if parent:
            self.get_ref().set_transient_for(parent)
        self.data = None

    def get_selection(self):
        dialog = self.get_ref()
        response = ANALYZER_SELECTION(dialog.run())
        dialog.hide()
        if response == ANALYZER_SELECTION.ANALYZE_FROM_AUDIT:
            self.data = self.get_object("auditLogTxt").get_text()
        return response

    def get_data(self):
        return self.data

    def on_auditLogTxt_icon_press(self, entry, icon_pos, *args):
        if icon_pos != Gtk.EntryIconPosition.SECONDARY:
            return

        fcd = Gtk.FileChooserDialog(
            title=OPEN_FILE_LABEL,
            transient_for=self.get_ref(),
            action=Gtk.FileChooserAction.OPEN,
        )
        fcd.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        response = fcd.run()
        fcd.hide()

        if response == Gtk.ResponseType.OK and path.isfile((fcd.get_filename())):
            self.get_object("auditLogTxt").set_text(fcd.get_filename())
        fcd.destroy()

    def on_auditLogTxt_changed(self, entry):
        self.get_object("analyzeAuditBtn").set_sensitive(entry.get_text())
