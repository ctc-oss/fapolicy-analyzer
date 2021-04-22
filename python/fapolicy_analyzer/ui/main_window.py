import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .ui_widget import UIWidget
from .database_admin_page import DatabaseAdminPage
from .analyzer_selection_dialog import AnalyzerSelectionDialog, ANALYZER_SELECTION
from .unapplied_changes_dialog import UnappliedChangesDialog
from .state_manager import stateManager


class MainWindow(UIWidget):
    def __init__(self):
        super().__init__()
        stateManager.changeset_queue_updated += self.on_changeset_updated
        self.window = self.builder.get_object("mainWindow")
        self.window.show_all()

<<<<<<< HEAD
    def __unapplied_changes(self):
        # Check backend for unapplied changes
        if not stateManager.is_dirty_queue():
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

=======
        # To support unapplied/unsaved changeset status in UI
        # Maintain original title, toplevel reference, register rate and fcn.
        self.windowTopLevel = self.window.get_toplevel()
        self.strTopLevelTitle = self.windowTopLevel.get_title()
        GLib.timeout_add_seconds(1, self.poll_backend_changeset)

    def poll_backend_changeset(self):
        if not Changeset().is_empty():
            self.set_modified_titlebar();
        else:
            self.set_modified_titlebar(False);
        return True

    def set_modified_titlebar(self, bModified = True):
        if(bModified):
            # Prefix title with '*'
            self.windowTopLevel.set_title("*"+self.strTopLevelTitle)
        else:
            # Reset title to original text
            self.windowTopLevel.set_title(self.strTopLevelTitle)

    def on_destroy(self, *args):
>>>>>>> Added polling to check for unapplied changes queue, and update titlebar appropriately.
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

    def on_changeset_updated(self):
        """The callback function invoked from the StateManager when
        state changes."""
        if stateManager.is_dirty_queue():
            print("main_window -> There are undeployed changes!")
        else:
            print("main_window -> There are no undeployed changes...")
