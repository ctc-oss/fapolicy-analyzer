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

        # To support unapplied/unsaved changeset status in UI
        # Maintain original title, toplevel reference
        self.windowTopLevel = self.window.get_toplevel()
        self.strTopLevelTitle = self.windowTopLevel.get_title()

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

        Gtk.main_quit()

    def on_delete_event(self, *args):
        return self.__unapplied_changes()

    def on_quitMenu_activate(self, menuItem, data=None):
        print("on_quitMenu_activate()")
        # Check backend for unapplied changes
        if not Changeset().is_empty():
            # Warn user pending changes will be lost.
            unapplied_changes_dlg = UnappliedChangesDialog(self.window)
            unappliedChangesDlg = unapplied_changes_dlg.get_content()
            response = unappliedChangesDlg.run()
            unappliedChangesDlg.destroy()

            # User returns to application
            if response != Gtk.ResponseType.OK:
                return True
        print("Terminating with unapplied changes...")
        return False

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

    def set_modified_titlebar(self, bModified=True):
        """Adds leading '*' to titlebar text with True or default argument"""
        if bModified:
            # Prefix title with '*'
            self.windowTopLevel.set_title("*"+self.strTopLevelTitle)
        else:
            # Reset title to original text
            self.windowTopLevel.set_title(self.strTopLevelTitle)

    def on_changeset_updated(self):
        """The callback function invoked from the StateManager when
        state changes."""
        if stateManager.is_dirty_queue():
            self.set_modified_titlebar(True)
        else:
            self.set_modified_titlebar(False)



