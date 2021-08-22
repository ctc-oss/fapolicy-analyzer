from os import path
import logging
import gi
import fapolicy_analyzer.ui.strings as strings

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from locale import gettext as _
from fapolicy_analyzer.util.format import f
from .analyzer_selection_dialog import ANALYZER_SELECTION  # , AnalyzerSelectionDialog
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
        self.mainContent = self.get_object("mainContent")

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

    def __apply_file_filters(self, dialog):
        fileFilterJson = Gtk.FileFilter()
        fileFilterJson.set_name(strings.FA_SESSION_FILES_FILTER_LABEL)
        fileFilterJson.add_pattern("*.json")
        dialog.add_filter(fileFilterJson)

        fileFilterAny = Gtk.FileFilter()
        fileFilterAny.set_name(strings.ANY_FILES_FILTER_LABEL)
        fileFilterAny.add_pattern("*")
        dialog.add_filter(fileFilterAny)

    def __pack_main_content(self, page):
        current = next(iter(self.mainContent.get_children()), None)
        if current:
            self.mainContent.remove(current)
        self.mainContent.pack_start(page, True, True, 0)

    def __auto_save_restore_dialog(self):
        """
        Presents a modal dialog alerting the user to the detection of an
        existing edit session autosaved files, prompting the user to invoke
        an immediate session restore, or to postpone or ignore the restore
        action.
        """

        dlgSessionRestorePrompt = Gtk.Dialog(
            title="Prior Session Detected", transient_for=self.window, flags=0
        )

        dlgSessionRestorePrompt.add_buttons(
            Gtk.STOCK_NO, Gtk.ResponseType.NO, Gtk.STOCK_YES, Gtk.ResponseType.YES
        )

        # dlgSessionRestorePrompt.set_default_size(-1, 200)
        label = Gtk.Label(label=strings.AUTOSAVE_ACTION_DIALOG_TEXT)
        hbox = dlgSessionRestorePrompt.get_content_area()
        hbox.add(label)
        dlgSessionRestorePrompt.show_all()
        response = dlgSessionRestorePrompt.run()
        dlgSessionRestorePrompt.destroy()
        return response

    def on_start(self, *args):
        # For now the analyzer selection dialog is just commented out so we can revert back to it if needed
        # selectionDlg = AnalyzerSelectionDialog(self.window)
        # page = router(selectionDlg.get_selection(), selectionDlg.get_data())
        page = router(ANALYZER_SELECTION.TRUST_DATABASE_ADMIN)
        self.mainContent.pack_start(page, True, True, 0)

        # On startup check for the existing of a tmp session file
        # If detected, alert the user, enable the File|Restore menu item
        if stateManager.detect_previous_session():
            logging.debug("Detected edit session tmp file")
            self.get_object("restoreMenu").set_sensitive(True)

            # Raise the modal  "Prior Session Detected" dialog to
            # prompt the user to immediate restore the prior edit session
            response = self.__auto_save_restore_dialog()

            if response == Gtk.ResponseType.YES:
                try:
                    if not stateManager.restore_previous_session():
                        stateManager.add_system_notification(
                            strings.AUTOSAVE_RESTORE_ERROR_MSG,
                            NotificationType.ERROR,
                        )

                    self.get_object("restoreMenu").set_sensitive(False)
                except Exception:
                    print("Restore failed")
        else:
            self.get_object("restoreMenu").set_sensitive(False)

    def on_destroy(self, obj, *args):
        if not isinstance(obj, Gtk.Window) and self.__unapplied_changes():
            return True

        Gtk.main_quit()

    def on_delete_event(self, *args):
        return self.__unapplied_changes()

    def on_changeset_updated(self):
        dirty = stateManager.is_dirty_queue()
        title = f"*{self.strTopLevelTitle}" if dirty else self.strTopLevelTitle
        self.windowTopLevel.set_title(title)

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
                        f(
                            _(
                                "An error occurred trying to open the session file, {self.strSessionFilename}"
                            )
                        ),
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

    def on_analyzeMenu_activate(self, menuitem, *args):
        fcd = Gtk.FileChooserDialog(
            title=strings.OPEN_FILE_LABEL,
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
            file = fcd.get_filename()
            self.__pack_main_content(
                router(ANALYZER_SELECTION.ANALYZE_FROM_AUDIT, file)
            )
        fcd.destroy()

    def on_trustDbMenu_activate(self, menuitem, *args):
        self.__pack_main_content(router(ANALYZER_SELECTION.TRUST_DATABASE_ADMIN))
