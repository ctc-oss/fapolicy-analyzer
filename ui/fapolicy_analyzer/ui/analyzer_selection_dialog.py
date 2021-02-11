import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from enum import Enum


class ANALYZER_SELECTION(Enum):
    TRUST_DATABASE_ADMIN = 0
    SCAN_SYSTEM = 1
    ANALYZE_FROM_AUDIT = 2


class AnalyzerSelectionDialog:
    def __init__(self, parent=None):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../glade/analyzer_selection_dialog.glade")
        self.builder.connect_signals(self)
        self.dialog = self.builder.get_object("analyzerSelectionDialog")
        if parent:
            self.dialog.set_transient_for(parent)

    def get_content(self):
        return self.dialog
