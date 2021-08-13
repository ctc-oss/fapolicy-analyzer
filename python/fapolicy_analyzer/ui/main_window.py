from os import path
import logging
import gi
import fapolicy_analyzer.ui.strings as strings

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .analyzer_selection_dialog import AnalyzerSelectionDialog, ANALYZER_SELECTION
from .database_admin_page import DatabaseAdminPage
from .notification import Notification
from .policy_rules_admin_page import PolicyRulesAdminPage
from .state_manager import stateManager, NotificationType
from .unapplied_changes_dialog import UnappliedChangesDialog
from .ui_widget import UIWidget


def router(selection, data=None):
    route = {
        ANALYZER_SELECTION.TRUST_DATABASE_ADMIN: DatabaseAdminPage,
        ANALYZER_SELECTION.SCAN_SYSTEM: PolicyRulesAdminPage,
        ANALYZER_SELECTION.ANALYZE_FROM_AUDIT: PolicyRulesAdminPage,
    }.get(selection)
    if route:
        return (route(data) if data else route()).get_ref()
    raise Exception("Bad Selection")


class MainWindow(UIWidget):
    def __init__(self):
        super().__init__()
        self.strSessionFilename = None
        stateManager.ev_changeset_queue_updated += self.on_changeset_updated
        self.window = self.get_ref()
        self.windowTopLevel = self.window.get_toplevel()
        self.strTopLevelTitle = self.windowTopLevel.get_title()

        toaster = Notification()
        self.get_object("overlay").add_overlay(toaster.get_ref())

        # Disable 'File' menu items until backend support is available
        self.get_object("restoreMenu").set_sensitive(False)

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

    def __apply_file_filters(self, dialog):
        fileFilterJson = Gtk.FileFilter()
        fileFilterJson.set_name(strings.FA_SESSION_FILES_FILTER_LABEL)
        fileFilterJson.add_pattern("*.json")
        dialog.add_filter(fileFilterJson)

        fileFilterAny = Gtk.FileFilter()
        fileFilterAny.set_name(strings.ANY_FILES_FILTER_LABEL)
        fileFilterAny.add_pattern("*")
        dialog.add_filter(fileFilterAny)

    def on_openMenu_activate(self, menuitem, data=None):
        logging.debug("Callback entered: MainWindow::on_openMenu_activate()")
        # Display file chooser dialog
        fcd = Gtk.FileChooserDialog(
            strings.OPEN_FILE_LABEL,
            self.windowTopLevel,
            Gtk.FileChooserAction.OPEN,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK,
            ),
        )
        self.__apply_file_filters(fcd)
        response = fcd.run()
        fcd.hide()

        if response == Gtk.ResponseType.OK:
            strFilename = fcd.get_filename()
            if path.isfile(strFilename):
                self.strSessionFilename = strFilename
                if not stateManager.open_edit_session(self.strSessionFilename):
                    stateManager.add_system_notification(
                        "An error occurred trying to open "
                        "the session file, {}".format(self.strSessionFilename),
                        NotificationType.ERROR,
                    )

        fcd.destroy()

    def on_restoreMenu_activate(self, menuitem, data=None):
        logging.debug("Callback entered: MainWindow::on_restoreMenu_activate()")
        try:
            if not stateManager.restore_previous_session():
                stateManager.add_system_notification(
                    "An error occurred trying to restore a prior "
                    "autosaved edit session ",
                    NotificationType.ERROR,
                )

        except Exception:
            print("Restore failed")

        # In all cases, gray out the File|Restore menu item
        self.get_object("restoreMenu").set_sensitive(False)

    def on_saveMenu_activate(self, menuitem, data=None):
        logging.debug("Callback entered: MainWindow::on_saveMenu_activate()")
        if not self.strSessionFilename:
            self.on_saveAsMenu_activate(menuitem, None)
        else:
            stateManager.save_edit_session(self.strSessionFilename)

    def on_saveAsMenu_activate(self, menuitem, data=None):
        logging.debug("Callback entered: MainWindow::on_saveAsMenu_activate()")
        # Display file chooser dialog
        fcd = Gtk.FileChooserDialog(
            strings.SAVE_AS_FILE_LABEL,
            self.windowTopLevel,
            Gtk.FileChooserAction.SAVE,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE,
                Gtk.ResponseType.OK,
            ),
        )

        self.__apply_file_filters(fcd)
        fcd.set_do_overwrite_confirmation(True)
        response = fcd.run()
        fcd.hide()

        if response == Gtk.ResponseType.OK:
            strFilename = fcd.get_filename()
            self.strSessionFilename = strFilename
            stateManager.save_edit_session(self.strSessionFilename)
            # Verify no exceptions
        fcd.destroy()

    def on_aboutMenu_activate(self, menuitem, data=None):
        aboutDialog = self.get_object("aboutDialog")
        aboutDialog.set_transient_for(self.window)
        aboutDialog.run()
        aboutDialog.hide()

    def on_start(self, *args):
        mainContent = self.get_object("mainContent")
        selectionDlg = AnalyzerSelectionDialog(self.window)
        page = router(selectionDlg.get_selection(), selectionDlg.get_data())
        mainContent.pack_start(page, True, True, 0)

        # On startup check for the existing of a tmp session file
        # If detected, alert the user, enable the File|Restore menu item
        if stateManager.detect_previous_session():
            logging.debug("Detected edit session tmp file")

            # Enable 'Restore' menu item under the 'File' menu
            self.get_object("restoreMenu").set_sensitive(True)

            # Raise the modal  "Prior Session Detected" dialog to
            # prompt the user to immediate restore the prior edit session
            response = self.__AutosaveRestoreDialog()

            if response == Gtk.ResponseType.YES:
                try:
                    if not stateManager.restore_previous_session():
                        stateManager.add_system_notification(
                            "An error occurred trying to restore a prior "
                            "autosaved edit session ",
                            NotificationType.ERROR,
                        )

                    self.get_object("restoreMenu").set_sensitive(False)
                except Exception:
                    print("Restore failed")
        else:
            self.get_object("restoreMenu").set_sensitive(False)

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
        logging.debug("MainWindow::on_changeset_updated()")
        state changes."""
        self.set_modified_titlebar(stateManager.is_dirty_queue())

    def __AutosaveRestoreDialog(self):
        """
        Presents a modal dialog alerting the user to the detection of an
        existing edit session autosaved files, prompting the user to invoke
        an immediate session restore, or to postpone or ignore the restore
        action.
        """

        dlgSessionRestorePrompt = Gtk.Dialog(title="Prior Session Detected",
                                             transient_for=self.window,
                                             flags=0
                                             )

        dlgSessionRestorePrompt.add_buttons(Gtk.STOCK_NO,
                                            Gtk.ResponseType.NO,
                                            Gtk.STOCK_YES,
                                            Gtk.ResponseType.YES)

        # dlgSessionRestorePrompt.set_default_size(-1, 200)
        label = Gtk.Label(label="""
        Restore your prior session now?

    Yes: Immediately loads your prior session

    No: Continue starting fapolicy-analyzer.

        Your prior session will still be available
        and can be loaded at any point during
        this current session by invoking 'Restore'
        under the 'File' menu.

        """)

        hbox = dlgSessionRestorePrompt.get_content_area()
        hbox.add(label)
        dlgSessionRestorePrompt.show_all()
        response = dlgSessionRestorePrompt.run()
        dlgSessionRestorePrompt.destroy()
        return response
