import context  # noqa: F401
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from helpers import delayed_gui_action
from ui.analyzer_selection_dialog import AnalyzerSelectionDialog, ANALYZER_SELECTION


def test_creates_widget():
    widget = AnalyzerSelectionDialog()
    assert type(widget.get_ref()) is Gtk.Dialog


def test_adds_dialog_to_parent():
    parent = Gtk.Window()
    widget = AnalyzerSelectionDialog(parent)
    assert widget.get_ref().get_transient_for() == parent


def test_trust_database_admin_selection():
    widget = AnalyzerSelectionDialog(Gtk.Window())
    trustAdminBtn = widget.get_object("adminTrustDatabasesBtn")
    delayed_gui_action(trustAdminBtn.clicked)
    result = widget.get_selection()
    assert result == ANALYZER_SELECTION.TRUST_DATABASE_ADMIN
