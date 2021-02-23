import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from database_admin_page import DatabaseAdminPage
from analyzer_selection_dialog import AnalyzerSelectionDialog, ANALYZER_SELECTION


class MainWindow:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../glade/main_window.glade")
        self.builder.connect_signals(self)

        self.window = self.builder.get_object("mainWindow")
        self.window.show_all()

    def on_destroy(self, *args):
        Gtk.main_quit()

    def on_aboutMenu_activate(self, menuitem, data=None):
        aboutDialog = self.builder.get_object("aboutDialog")
        aboutDialog.set_transient_for(self.window)
        aboutDialog.run()
        aboutDialog.hide()

    def on_start(self, *args):
        analyserSelectionDialog = AnalyzerSelectionDialog(self.window).get_content()
        response = analyserSelectionDialog.run()
        analyserSelectionDialog.hide()

        if ANALYZER_SELECTION(response) == ANALYZER_SELECTION.TRUST_DATABASE_ADMIN:
            page = DatabaseAdminPage().get_content()
        else:
            raise Exception("Bad Selection")

        mainContent = self.builder.get_object("mainContent")
        mainContent.pack_start(page, True, True, 0)
