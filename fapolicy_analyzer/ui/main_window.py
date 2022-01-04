# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
from locale import gettext as _
from os import path, geteuid, getenv

from enum import Enum
from fapolicy_analyzer import Handle

import fapolicy_analyzer.ui.strings as strings
import gi
from fapolicy_analyzer.util.format import f
from threading import Thread, Lock
from time import sleep
from typing import NamedTuple

from .actions import NotificationType, add_notification
from .analyzer_selection_dialog import ANALYZER_SELECTION
from .database_admin_page import DatabaseAdminPage
from .notification import Notification
from .operations import DeployChangesetsOp
from .policy_rules_admin_page import PolicyRulesAdminPage
from .session_manager import sessionManager
from .store import dispatch, get_system_feature
from .ui_widget import UIConnectedWidget
from .unapplied_changes_dialog import UnappliedChangesDialog

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib  # isort: skip


def router(selection, data=None):
    route = {
        ANALYZER_SELECTION.TRUST_DATABASE_ADMIN: DatabaseAdminPage,
        ANALYZER_SELECTION.SCAN_SYSTEM: PolicyRulesAdminPage,
        ANALYZER_SELECTION.ANALYZE_FROM_AUDIT: PolicyRulesAdminPage,
        ANALYZER_SELECTION.ANALYZE_SYSLOG: PolicyRulesAdminPage,
    }.get(selection)
    if route:
        return route(data) if data else route()
    raise Exception("Bad Selection")


class ServiceStatus(Enum):
    TRUE = True
    FALSE = False
    UNKNOWN = None


class DaemonState(NamedTuple):
    error: str
    status: ServiceStatus


class MainWindow(UIConnectedWidget):
    def __init__(self):
        super().__init__(get_system_feature(), on_next=self.on_next_system)
        self.strSessionFilename = None
        self.window = self.get_ref()
        self.windowTopLevel = self.window.get_toplevel()
        self.strTopLevelTitle = self.windowTopLevel.get_title()
        self.fapdStatusLight = self.get_object("fapdStatusLight")
        self._fapdControlPermitted = (geteuid() == 0)  # set if root user
        self._fapdStartMenuItem = self.get_object("fapdStartMenu")
        self._fapdStopMenuItem = self.get_object("fapdStopMenu")
        self._fapd_status = ServiceStatus.UNKNOWN
        self._fapd_monitoring = False
        self._fapd_ref = None
        self._fapd_lock = Lock()
        self._changesets = []
        self._page = None

        toaster = Notification()
        self.get_object("overlay").add_overlay(toaster.get_ref())
        self.mainContent = self.get_object("mainContent")

        # Set menu items in default initial state
        self.get_object("restoreMenu").set_sensitive(False)
        self.__set_trustDbMenu_sensitive(False)

        # Set fapd status UI element to default 'No' = Red button
        self.fapdStatusLight.set_from_stock(stock_id="gtk-no", size=4)

        # Set initial fapd menu item state
        self._fapdStartMenuItem.set_sensitive(False)
        self._fapdStopMenuItem.set_sensitive(False)

        self.window.show_all()

    def __unapplied_changes(self):
        # Check backend for unapplied changes
        if not self._changesets:
            return False

        # Warn user pending changes will be lost.
        unapplied_changes_dlg = UnappliedChangesDialog(self.window)
        unappliedChangesDlg = unapplied_changes_dlg.get_ref()
        response = unappliedChangesDlg.run()
        unappliedChangesDlg.destroy()
        return response != Gtk.ResponseType.OK

    def __apply_json_file_filters(self, dialog):
        fileFilterJson = Gtk.FileFilter()
        fileFilterJson.set_name(strings.FA_SESSION_FILES_FILTER_LABEL)
        fileFilterJson.add_pattern("*.json")
        dialog.add_filter(fileFilterJson)

        fileFilterAny = Gtk.FileFilter()
        fileFilterAny.set_name(strings.ANY_FILES_FILTER_LABEL)
        fileFilterAny.add_pattern("*")
        dialog.add_filter(fileFilterAny)

    def __pack_main_content(self, page):
        if self._page:
            self._page.dispose()
        self._page = page
        self.mainContent.pack_start(page.get_ref(), True, True, 0)

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

    def __set_trustDbMenu_sensitive(self, sensitive):
        menuItem = self.get_object("trustDbMenu")
        menuItem.set_sensitive(sensitive)

    def on_start(self, *args):
        self.__pack_main_content(router(ANALYZER_SELECTION.TRUST_DATABASE_ADMIN))

        # On startup check for the existing of a tmp session file
        # If detected, alert the user, enable the File|Restore menu item
        if sessionManager.detect_previous_session():
            logging.debug("Detected edit session tmp file")
            self.get_object("restoreMenu").set_sensitive(True)

            # Raise the modal  "Prior Session Detected" dialog to
            # prompt the user to immediate restore the prior edit session
            response = self.__auto_save_restore_dialog()

            if response == Gtk.ResponseType.YES:
                try:
                    if not sessionManager.restore_previous_session():
                        dispatch(
                            add_notification(
                                strings.AUTOSAVE_RESTORE_ERROR_MSG,
                                NotificationType.ERROR,
                            )
                        )

                    self.get_object("restoreMenu").set_sensitive(False)
                except Exception:
                    print("Restore failed")
        else:
            self.get_object("restoreMenu").set_sensitive(False)

        # Initialize and start fapd status monitoring
        self.init_daemon()
        if getenv("DISABLE_DAEMON_MONITORING", "false").lower() == "false":
            self._start_daemon_monitor()

    def on_destroy(self, obj, *args):
        if not isinstance(obj, Gtk.Window) and self.__unapplied_changes():
            return True

        Gtk.main_quit()

    def on_delete_event(self, *args):
        return self.__unapplied_changes()

    def on_next_system(self, system):
        self._changesets = system["changesets"]
        dirty = len(self._changesets) > 0
        title = f"*{self.strTopLevelTitle}" if dirty else self.strTopLevelTitle
        self.windowTopLevel.set_title(title)
        self.get_object("deployChanges").set_sensitive(dirty)

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
        self.__apply_json_file_filters(fcd)
        response = fcd.run()
        fcd.hide()

        if response == Gtk.ResponseType.OK:
            strFilename = fcd.get_filename()
            if path.isfile(strFilename):
                self.strSessionFilename = strFilename
                if not sessionManager.open_edit_session(self.strSessionFilename):
                    dispatch(
                        add_notification(
                            f(
                                _(
                                    "An error occurred trying to open the session file, {self.strSessionFilename}"
                                )
                            ),
                            NotificationType.ERROR,
                        )
                    )

        fcd.destroy()

    def on_restoreMenu_activate(self, menuitem, data=None):
        logging.debug("Callback entered: MainWindow::on_restoreMenu_activate()")
        try:
            if not sessionManager.restore_previous_session():
                dispatch(
                    add_notification(
                        strings.AUTOSAVE_RESTORE_ERROR_MSG,
                        NotificationType.ERROR,
                    )
                )

        except Exception:
            logging.exception("Restore failed")

        # In all cases, gray out the File|Restore menu item
        self.get_object("restoreMenu").set_sensitive(False)

    def on_saveMenu_activate(self, menuitem, data=None):
        logging.debug("Callback entered: MainWindow::on_saveMenu_activate()")
        if not self.strSessionFilename:
            self.on_saveAsMenu_activate(menuitem, None)
        else:
            sessionManager.save_edit_session(
                self._changesets,
                self.strSessionFilename,
            )

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

        self.__apply_json_file_filters(fcd)
        fcd.set_do_overwrite_confirmation(True)
        response = fcd.run()
        fcd.hide()

        if response == Gtk.ResponseType.OK:
            strFilename = fcd.get_filename()
            self.strSessionFilename = strFilename
            sessionManager.save_edit_session(
                self._changesets,
                self.strSessionFilename,
            )

        fcd.destroy()

    def on_aboutMenu_activate(self, *args):
        aboutDialog = self.get_object("aboutDialog")
        aboutDialog.set_transient_for(self.window)
        aboutDialog.run()
        aboutDialog.hide()

    def on_syslogMenu_activate(self, *args):
        self.__pack_main_content(router(ANALYZER_SELECTION.ANALYZE_SYSLOG))
        self.__set_trustDbMenu_sensitive(True)

    def on_analyzeMenu_activate(self, *args):
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
            self.__set_trustDbMenu_sensitive(True)
        fcd.destroy()

    def on_trustDbMenu_activate(self, menuitem, *args):
        self.__pack_main_content(router(ANALYZER_SELECTION.TRUST_DATABASE_ADMIN))
        self.__set_trustDbMenu_sensitive(False)

    def on_deployChanges_clicked(self, *args):
        with DeployChangesetsOp(self.window) as op:
            op.run(self._changesets)

# ###################### fapolicyd interfacing ##########################
    def on_fapdStartMenu_activate(self, menuitem, data=None):
        logging.debug("on_fapdStartMenu_activate() invoked.")
        if (self._fapd_status != ServiceStatus.UNKNOWN) and (self._fapd_lock.acquire()):
            self._fapd_ref.start()
            self._fapd_lock.release()

    def on_fapdStopMenu_activate(self, menuitem, data=None):
        logging.debug("on_fapdStopMenu_activate() invoked.")
        if (self._fapd_status != ServiceStatus.UNKNOWN) and (self._fapd_lock.acquire()):
            self._fapd_ref.stop()
            self._fapd_lock.release()

    def _enable_fapd_menu_items(self, status):
        if self._fapdControlPermitted and (status != ServiceStatus.UNKNOWN):
            self._fapdStartMenuItem.set_sensitive(not status)
            self._fapdStopMenuItem.set_sensitive(status)
        else:
            self._fapdStartMenuItem.set_sensitive(False)
            self._fapdStopMenuItem.set_sensitive(False)

    def _update_fapd_status(self, status: ServiceStatus):
        logging.debug(f"__update_fapd_status({status})")

        # Enable/Disable fapd menu items
        self._enable_fapd_menu_items(status)
        if status is True:
            self.fapdStatusLight.set_from_stock(stock_id="gtk-yes", size=4)
        elif status is False:
            self.fapdStatusLight.set_from_stock(stock_id="gtk-no", size=4)
        else:
            self.fapdStatusLight.set_from_stock(stock_id="gtk-no", size=4)

    def init_daemon(self):
        if self._fapd_lock.acquire():
            self._fapd_ref = Handle("fapolicyd")
            if self._fapd_ref.is_valid():
                self._fapd_status = self._fapd_ref.is_active()
            else:
                self._fapd_status = ServiceStatus.UNKNOWN
            self.on_update_daemon_status(self._fapd_status)
            self._fapd_lock.release()

    def on_update_daemon_status(self, status: ServiceStatus):
        logging.debug(f"on_update_daemon_status({status})")
        self._fapd_status = status
        GLib.idle_add(self._update_fapd_status, status)

    def _monitor_daemon(self, timeout=5):
        logging.debug("_monitor_daemon() executing")
        while True:
            try:
                if self._fapd_lock.acquire(blocking=False):
                    bStatus = self._fapd_ref.is_active()
                    if bStatus != self._fapd_status:
                        logging.debug("monitor_daemon:Dispatch update request")
                        self.on_update_daemon_status(bStatus)
                    self._fapd_lock.release()
            except Exception:
                print("Daemon monitor query/update dispatch failed.")
            sleep(timeout)

    def _start_daemon_monitor(self):
        logging.debug(f"start_daemon_monitor(): {self._fapd_status}")
        # Only start monitoring thread if fapolicy is installed
        if self._fapd_status is not ServiceStatus.UNKNOWN:
            logging.debug("Spawning monitor thread...")
            thread = Thread(target=self._monitor_daemon)
            thread.daemon = True
            thread.start()
            self._fapd_monitoring = True
            logging.debug(f"Thread={thread}, Running={self._fapd_monitoring}")
