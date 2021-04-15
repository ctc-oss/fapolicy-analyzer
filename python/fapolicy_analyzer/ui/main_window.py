import gi
import time

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .ui_widget import UIWidget
from .database_admin_page import DatabaseAdminPage
from .analyzer_selection_dialog import AnalyzerSelectionDialog, ANALYZER_SELECTION
from .unapplied_changes_dialog import UnappliedChangesDialog
from fapolicy_analyzer import Changeset


class MainWindow(UIWidget):
    def __init__(self):
        super().__init__()
        self.window = self.builder.get_object("mainWindow")
        self.window.show_all()

    def __unapplied_changes(self):
        # Check backend for unapplied changes
        if not Changeset().is_empty():
            return False

        # Warn user pending changes will be lost.
        unapplied_changes_dlg = UnappliedChangesDialog(self.window)
        unappliedChangesDlg = unapplied_changes_dlg.get_content()
        response = unappliedChangesDlg.run()
        unappliedChangesDlg.destroy()
        return response != Gtk.ResponseType.OK

    def on_destroy(self, obj, *args):
        if not isinstance(obj, Gtk.Window) and self.__unapplied_changes():
            return True

        Gtk.main_quit()

    def on_delete_event(self, *args):
        return self.__unapplied_changes()

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
