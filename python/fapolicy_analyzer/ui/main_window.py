import logging
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .analyzer_selection_dialog import AnalyzerSelectionDialog, ANALYZER_SELECTION
from .database_admin_page import DatabaseAdminPage
from .notification import Notification
from .state_manager import stateManager
from .unapplied_changes_dialog import UnappliedChangesDialog
from .ui_widget import UIWidget


def router(selection):
    route = {ANALYZER_SELECTION.TRUST_DATABASE_ADMIN: DatabaseAdminPage}.get(selection)
    if route:
        return route().get_ref()
    raise Exception("Bad Selection")


class MainWindow(UIWidget):
    def __init__(self):
        super().__init__()
        stateManager.changeset_queue_updated += self.on_changeset_updated
        self.window = self.get_ref()
        self.windowTopLevel = self.window.get_toplevel()
        self.strTopLevelTitle = self.windowTopLevel.get_title()

        toaster = Notification()
        self.get_object("overlay").add_overlay(toaster.get_ref())

        # Disable 'File' menu items until backend support is available
        self.get_object("openMenu").set_sensitive(False)
        self.get_object("restoreMenu").set_sensitive(False)
        self.get_object("saveMenu").set_sensitive(False)
        self.get_object("saveAsMenu").set_sensitive(False)

        self.window.show_all()

    def __unapplied_changes(self):
        # Check backend for unapplied changes
        if not stateManager.is_dirty_queue():
            return False

        # Warn user pending changes will be lost.
        unapplied_changes_dlg = UnappliedChangesDialog(self.window)
        unappliedChangesDlg = unapplied_changes_dlg.get_ref()
        response = unappliedChangesDlg.run()
        unappliedChangesDlg.destroy()
        return response != Gtk.ResponseType.OK

    def on_destroy(self, obj, *args):
        if not isinstance(obj, Gtk.Window) and self.__unapplied_changes():
            return True

        Gtk.main_quit()

    def on_delete_event(self, *args):
        return self.__unapplied_changes()

    def on_openMenu_activate(self, menuitem, data=None):
        logging.debug("Callback entered: MainWindow::on_openMenu_activate()")
        pass

    def on_restoreMenu_activate(self, menuitem, data=None):
        logging.debug("Callback entered: MainWindow::on_restoreMenu_activate()")
        pass

    def on_saveMenu_activate(self, menuitem, data=None):
        logging.debug("Callback entered: MainWindow::on_saveMenu_activate()")
        pass

    def on_saveAsMenu_activate(self, menuitem, data=None):
        logging.debug("Callback entered: MainWindow::on_saveAsMenu_activate()")
        pass

    def on_aboutMenu_activate(self, menuitem, data=None):
        aboutDialog = self.get_object("aboutDialog")
        aboutDialog.set_transient_for(self.window)
        aboutDialog.run()
        aboutDialog.hide()

    def on_start(self, *args):
        mainContent = self.get_object("mainContent")
        selection = AnalyzerSelectionDialog(self.window).get_selection()
        page = router(selection)
        mainContent.pack_start(page, True, True, 0)

    def set_modified_titlebar(self, bModified=True):
        """Adds leading '*' to titlebar text with True or default argument"""
        if bModified:
            # Prefix title with '*'
            self.windowTopLevel.set_title("*" + self.strTopLevelTitle)
        else:
            # Reset title to original text
            self.windowTopLevel.set_title(self.strTopLevelTitle)

    def on_changeset_updated(self):
        """The callback function invoked from the StateManager when
        state changes."""
        self.set_modified_titlebar(stateManager.is_dirty_queue())
