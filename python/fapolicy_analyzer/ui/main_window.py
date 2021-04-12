import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .ui_widget import UIWidget
from .database_admin_page import DatabaseAdminPage
from .analyzer_selection_dialog import AnalyzerSelectionDialog, ANALYZER_SELECTION
from .unapplied_changes_dialog import UnappliedChangesDialog

#from fapolicy_analyzer import PyChangeSet

class MainWindow(UIWidget):
    def __init__(self):
        super().__init__()
        self.window = self.builder.get_object("mainWindow")
        self.window.show_all()

    def on_destroy(self, *args):
        # Check backend for unapplied changes
        if(True):
            unappliedChangesDlg = UnappliedChangesDialog(self.window).get_content()
            response = unappliedChangesDlg.run()
            unappliedChangesDlg.destroy()
            if response != Gtk.ResponseType.OK:
                # Otherwise we keep the application open
                return True

        print('Terminating...')
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

        if response == ANALYZER_SELECTION.TRUST_DATABASE_ADMIN.value:
            page = DatabaseAdminPage().get_content()
        else:
            raise Exception("Bad Selection")

        mainContent = self.builder.get_object("mainContent")
        mainContent.pack_start(page, True, True, 0)
