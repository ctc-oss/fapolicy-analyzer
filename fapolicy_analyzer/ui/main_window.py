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
from os import getenv, geteuid, path
from threading import Thread
from time import sleep
from typing import Any, Sequence

import fapolicy_analyzer.ui.strings as strings
import gi
from fapolicy_analyzer import System
from fapolicy_analyzer import __version__ as app_version
from fapolicy_analyzer.ui.action_toolbar import ActionToolbar
from fapolicy_analyzer.ui.actions import NotificationType, add_notification
from fapolicy_analyzer.ui.analyzer_selection_dialog import ANALYZER_SELECTION
from fapolicy_analyzer.ui.changeset_wrapper import Changeset
from fapolicy_analyzer.ui.configs import Sizing
from fapolicy_analyzer.ui.database_admin_page import DatabaseAdminPage
from fapolicy_analyzer.ui.fapd_manager import FapdManager, ServiceStatus
from fapolicy_analyzer.ui.notification import Notification
from fapolicy_analyzer.ui.operations import DeployChangesetsOp
from fapolicy_analyzer.ui.policy_rules_admin_page import PolicyRulesAdminPage
from fapolicy_analyzer.ui.profiler_page import ProfilerPage
from fapolicy_analyzer.ui.rules import RulesAdminPage
from fapolicy_analyzer.ui.session_manager import sessionManager
from fapolicy_analyzer.ui.store import dispatch, get_system_feature
from fapolicy_analyzer.ui.ui_page import UIAction, UIPage
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget
from fapolicy_analyzer.ui.unapplied_changes_dialog import UnappliedChangesDialog
from fapolicy_analyzer.util.format import f

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib  # isort: skip


def router(selection: ANALYZER_SELECTION, data: Any = None) -> UIPage:
    route = {
        ANALYZER_SELECTION.TRUST_DATABASE_ADMIN: DatabaseAdminPage,
        ANALYZER_SELECTION.ANALYZE_FROM_AUDIT: PolicyRulesAdminPage,
        ANALYZER_SELECTION.ANALYZE_SYSLOG: PolicyRulesAdminPage,
        ANALYZER_SELECTION.RULES_ADMIN: RulesAdminPage,
        ANALYZER_SELECTION.PROFILER: ProfilerPage,
    }.get(selection)
    if route:
        return route(data) if data else route()
    raise Exception("Bad Selection")


class MainWindow(UIConnectedWidget):
    def __init__(self):
        super().__init__(get_system_feature(), on_next=self.on_next_system)
        self.strSessionFilename = None
        self.window = self.get_ref()
        self.windowTopLevel = self.window.get_toplevel()
        self.strTopLevelTitle = self.windowTopLevel.get_title()
        self.fapdStatusLight = self.get_object("fapdStatusLight")
        self._fapdControlPermitted = geteuid() == 0  # set if root user
        self._fapdStartMenuItem = self.get_object("fapdStartMenu")
        self._fapdStopMenuItem = self.get_object("fapdStopMenu")
        self._fapd_status = ServiceStatus.UNKNOWN
        self._fapd_monitoring = False
        self._fapd_mgr = FapdManager(self._fapdControlPermitted)
        self.__changesets: Sequence[Changeset] = []
        self.__system: System
        self.__checkpoint: System
        self.__page = None

        toaster = Notification(timer_duration=5)
        self.get_object("overlay").add_overlay(toaster.get_ref())
        self.mainContent = self.get_object("mainContent")
        # Set menu items in default initial state
        self.get_object("restoreMenu").set_sensitive(False)
        self.__set_trustDbMenu_sensitive(False)

        # Set fapd status UI element to default 'No' = Red button
        self.fapdStatusLight.set_from_icon_name("process-stop", size=4)

        # Set initial fapd menu items state
        self._fapdStartMenuItem.set_sensitive(False)
        self._fapdStopMenuItem.set_sensitive(False)

        # Enable profiler tool menu item if root user, env var, or magic file
        prof_ui_enable = (
            self._fapdControlPermitted  # EUID == 0
            or getenv("PROF_UI_ENABLE", "false").lower() != "false"
            or path.exists("/tmp/prof_ui_enable")
        )
        self.get_object("profileExecMenu").set_sensitive(prof_ui_enable)

        self.__add_toolbar()
        self.window.show_all()

    def __add_toolbar(self):
        # Set of actions available to all UIPages
        self.__actions = {
            "actions": [
                UIAction(
                    name="Deploy",
                    tooltip="Deploy Changesets",
                    icon="system-software-update",
                    signals={"clicked": self.on_deployChanges_clicked},
                    sensitivity_func=self.__dirty_changesets,
                )
            ],
        }
        self.__toolbar = ActionToolbar(self.__actions)
        app_area = self.get_object("appArea")
        app_area.pack_start(self.__toolbar, False, True, 0)
        app_area.reorder_child(self.__toolbar, 1)

    def __unapplied_changes(self):
        # Check backend for unapplied changes
        if not self.__changesets:
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

    def __pack_main_content(self, page: UIPage):
        if self.__page:
            self.__page.dispose()
        self.__page = page
        self.mainContent.pack_start(page.get_ref(), True, True, 0)

        actions = UIPage.merge_actions(self.__actions, page.actions)
        self.__toolbar.rebuild_toolbar(actions)

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

    def __dirty_changesets(self):
        return len(self.__changesets) > 0

    def on_start(self, *args):
        logging.debug(f"MainWindow::on_start({args})")
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
                    logging.debug("Restore failed")
        else:
            self.get_object("restoreMenu").set_sensitive(False)

        # Initialize and start fapd status monitoring
        self.init_fapd_state()
        if getenv("DISABLE_DAEMON_MONITORING", "false").lower() == "false":
            logging.debug("Starting the fapd monitoring thread")
            self._start_daemon_monitor()

    def on_destroy(self, obj, *args):
        if not isinstance(obj, Gtk.Window) and self.__unapplied_changes():
            return True

        Gtk.main_quit()

    def on_delete_event(self, *args):
        return self.__unapplied_changes()

    def on_next_system(self, system):
        self.__changesets = system["changesets"].changesets
        self.__system = system["system"].system
        self.__checkpoint = system["system"].checkpoint
        dirty = self.__dirty_changesets()
        title = f"*{self.strTopLevelTitle}" if dirty else self.strTopLevelTitle
        self.windowTopLevel.set_title(title)
        self.__toolbar.refresh_buttons_sensitivity()

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
                self.__changesets,
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
                self.__changesets,
                self.strSessionFilename,
            )

        fcd.destroy()

    def on_aboutMenu_activate(self, *args):
        aboutDialog = self.get_object("aboutDialog")
        aboutDialog.set_transient_for(self.window)
        aboutDialog.set_version(f"v{app_version}")
        aboutDialog.run()
        aboutDialog.hide()

    def on_helpMenu_activate(self, *args):
        # if meld.conf.DATADIR_IS_UNINSTALLED:
        #     uri = "http://meldmerge.org/help/"
        # else:
        #     uri = "help:meld"
        uri = "help:fapolicy-analyzer/Home.docbook"
        Gtk.show_uri_on_window(self.window, uri, Gtk.get_current_event_time())

    def on_syslogMenu_activate(self, *args):
        page = router(ANALYZER_SELECTION.ANALYZE_SYSLOG)
        height = self.get_object("mainWindow").get_size()[1]
        page.get_object("botBox").set_property(
            "height_request", int(height * Sizing.POLICY_BOTTOM_BOX)
        )
        self.__pack_main_content(page)
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
            page = router(ANALYZER_SELECTION.ANALYZE_FROM_AUDIT, file)
            page.object_list.rule_view_activate += self.on_rulesAdminMenu_activate
            height = self.get_object("mainWindow").get_size()[1]
            page.get_object("botBox").set_property(
                "height_request", int(height * Sizing.POLICY_BOTTOM_BOX)
            )
            self.__pack_main_content(page)
            self.__set_trustDbMenu_sensitive(True)
        fcd.destroy()

    def activate_file_analyzer(self, file):
        self.__pack_main_content(router(ANALYZER_SELECTION.ANALYZE_FROM_AUDIT, file))
        self.__set_trustDbMenu_sensitive(True)

    def on_trustDbMenu_activate(self, menuitem, *args):
        self.__pack_main_content(router(ANALYZER_SELECTION.TRUST_DATABASE_ADMIN))
        self.__set_trustDbMenu_sensitive(False)

    def on_rulesAdminMenu_activate(self, *args, **kwargs):
        rulesPage = router(ANALYZER_SELECTION.RULES_ADMIN)
        if kwargs.get("rule_id", None) is not None:
            rulesPage.highlight_row_from_data(kwargs["rule_id"])
        self.__pack_main_content(rulesPage)
        # TODO: figure out a good way to set sensitivity on the menu items based on what is selected
        self.__set_trustDbMenu_sensitive(True)

    def on_profileExecMenu_activate(self, *args):
        page = router(ANALYZER_SELECTION.PROFILER, self._fapd_mgr)
        page.analyze_button_pushed += self.activate_file_analyzer
        page.refresh_toolbar += self._refresh_toolbar
        self.__pack_main_content(page)
        self.__set_trustDbMenu_sensitive(True)

    def _refresh_toolbar(self):
        self.__toolbar.refresh_buttons_sensitivity()

    def on_deployChanges_clicked(self, *args):
        with DeployChangesetsOp(self.window) as op:
            op.run(self.__changesets, self.__system, self.__checkpoint)

    # ###################### fapolicyd interfacing ##########################
    def on_fapdStartMenu_activate(self, menuitem, data=None):
        logging.debug("on_fapdStartMenu_activate() invoked.")
        if self._fapd_status != ServiceStatus.UNKNOWN:
            self._fapd_mgr.start()

    def on_fapdStopMenu_activate(self, menuitem, data=None):
        logging.debug("on_fapdStopMenu_activate() invoked.")
        if self._fapd_status != ServiceStatus.UNKNOWN:
            self._fapd_mgr.stop()

    def _enable_fapd_menu_items(self, status: ServiceStatus):
        if self._fapdControlPermitted and (status != ServiceStatus.UNKNOWN):
            # Convert ServiceStatus to bool
            if status == ServiceStatus.TRUE:
                bStatus = True
            else:
                bStatus = False
            self._fapdStartMenuItem.set_sensitive(not bStatus)
            self._fapdStopMenuItem.set_sensitive(bStatus)
        else:
            self._fapdStartMenuItem.set_sensitive(False)
            self._fapdStopMenuItem.set_sensitive(False)

    def _update_fapd_status(self, status: ServiceStatus):
        logging.debug(f"_update_fapd_status({status})")

        # Enable/Disable fapd menu items
        self._enable_fapd_menu_items(status)
        if status is ServiceStatus.TRUE:
            self.fapdStatusLight.set_from_icon_name("emblem-default", size=4)
        elif status is ServiceStatus.FALSE:
            self.fapdStatusLight.set_from_icon_name("process-stop", size=4)
        else:
            self.fapdStatusLight.set_from_icon_name("edit-delete", size=4)

    def init_fapd_state(self):
        self._fapd_status = self._fapd_mgr.status()
        self.on_update_daemon_status(self._fapd_status)

    def on_update_daemon_status(self, status: ServiceStatus):
        logging.debug(f"on_update_daemon_status({status})")
        self._fapd_status = status
        GLib.idle_add(self._update_fapd_status, status)

    def _monitor_daemon(self, timeout=5):
        logging.debug("_monitor_daemon() executing")
        while True:
            try:
                bStatus = self._fapd_mgr.status()
                if bStatus != self._fapd_status:
                    logging.debug("monitor_daemon:Dispatch update request")
                    self.on_update_daemon_status(bStatus)
            except Exception:
                print("Daemon monitor query/update dispatch failed.")
            sleep(timeout)

    def _start_daemon_monitor(self):
        logging.debug(f"start_daemon_monitor(): {self._fapd_status}")
        # Only start monitoring thread if fapolicyd is installed
        if self._fapd_status is not ServiceStatus.UNKNOWN:
            logging.debug("Spawning monitor thread...")
            thread = Thread(target=self._monitor_daemon)
            thread.daemon = True
            thread.start()
            self._fapd_monitoring = True
            logging.debug(f"Thread={thread}, Running={self._fapd_monitoring}")
