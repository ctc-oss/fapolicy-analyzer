# Copyright Concurrent Technologies Corporation 2023
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
import os
from locale import gettext as _
from os import getenv, geteuid, path
from threading import Thread
from time import sleep
from typing import Sequence

import gi

import fapolicy_analyzer.ui.strings as strings
from fapolicy_analyzer import System
from fapolicy_analyzer import __version__ as app_version
from fapolicy_analyzer.ui.action_toolbar import ActionToolbar
from fapolicy_analyzer.ui.actions import (
    NotificationType,
    add_notification,
    request_ancillary_trust,
    request_app_config,
    request_system_trust,
)
from fapolicy_analyzer.ui.changeset_wrapper import Changeset
from fapolicy_analyzer.ui.configs import Sizing
from fapolicy_analyzer.ui.database_admin_page import DatabaseAdminPage
from fapolicy_analyzer.ui.fapd_manager import FapdManager, ServiceStatus
from fapolicy_analyzer.ui.file_chooser_dialog import FileChooserDialog
from fapolicy_analyzer.ui.help_browser import HelpBrowser
from fapolicy_analyzer.ui.notification import Notification
from fapolicy_analyzer.ui.operations import DeployChangesetsOp
from fapolicy_analyzer.ui.policy_rules_admin_page import PolicyRulesAdminPage
from fapolicy_analyzer.ui.profiler_page import ProfilerPage
from fapolicy_analyzer.ui.rules import RulesAdminPage
from fapolicy_analyzer.ui.session_manager import sessionManager
from fapolicy_analyzer.ui.store import (
    dispatch,
    get_application_feature,
    get_system_feature,
)
from fapolicy_analyzer.ui.types import PAGE_SELECTION
from fapolicy_analyzer.ui.ui_page import UIAction, UIPage
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget
from fapolicy_analyzer.ui.unapplied_changes_dialog import UnappliedChangesDialog
from fapolicy_analyzer.util.format import f

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib  # isort: skip


def router(page: PAGE_SELECTION, *data) -> UIPage:
    data = (d for d in data if d is not None)
    route = {
        PAGE_SELECTION.TRUST_DATABASE_ADMIN: DatabaseAdminPage,
        PAGE_SELECTION.ANALYZE_FROM_DEBUG: PolicyRulesAdminPage,
        PAGE_SELECTION.ANALYZE_SYSLOG: PolicyRulesAdminPage,
        PAGE_SELECTION.ANALYZE_AUDIT: PolicyRulesAdminPage,
        PAGE_SELECTION.RULES_ADMIN: RulesAdminPage,
        PAGE_SELECTION.PROFILER: ProfilerPage,
    }.get(page, RulesAdminPage)
    return route(*data)


class MainWindow(UIConnectedWidget):

    __JSON_FILE_FILTERS = [
        (strings.FA_SESSION_FILES_FILTER_LABEL, "*.json"),
        (strings.ANY_FILES_FILTER_LABEL, "*"),
    ]

    def __init__(self):
        features = [
            {get_system_feature(): {"on_next": self.on_next_system}},
            {get_application_feature(): {"on_next": self.on_next_application}},
        ]
        super().__init__(features=features)
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
        self.__application = None
        self.__page = None
        self.__help = None

        toaster = Notification(timer_duration=5)
        self.get_object("overlay").add_overlay(toaster.get_ref())
        self.mainContent = self.get_object("mainContent")
        # Set menu items in default initial state
        self.get_object("restoreMenu").set_sensitive(False)

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

        # load app config
        dispatch(request_app_config())

        # start trust loading
        dispatch(request_system_trust())
        dispatch(request_ancillary_trust())

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

    def __dirty_changesets(self):
        return len(self.__changesets) > 0

    def on_start(self, *args):
        logging.info("MainWindow::on_start()")

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

        if self.__help:
            self.__help.destroy()

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

    def on_next_application(self, application):
        if self.__application != application:
            self.__application = application

            try:
                selection = PAGE_SELECTION(application.initial_view)
            except ValueError:
                logging.warning(
                    f"Invalid initial page set to {application.initial_view}"
                )
                selection = PAGE_SELECTION.RULES_ADMIN

            # TODO: Need to figure out a better way to handle pages that need extra parameters
            data = {
                PAGE_SELECTION.PROFILER: self._fapd_mgr,
                PAGE_SELECTION.ANALYZE_SYSLOG: True,
            }.get(selection)
            page = router(selection, data)
            self.__pack_main_content(page)

            if selection == PAGE_SELECTION.PROFILER:
                page.analyze_button_pushed += self.activate_file_analyzer
                page.refresh_toolbar += self._refresh_toolbar

    def on_openMenu_activate(self, menuitem, data=None):
        logging.debug("Callback entered: MainWindow::on_openMenu_activate()")
        # Display file chooser dialog
        fcd = FileChooserDialog(
            title=strings.OPEN_FILE_LABEL,
            parent=self.get_ref(),
            filters=self.__JSON_FILE_FILTERS,
        )

        strFilename = fcd.get_filename() or ""
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
        fcd = FileChooserDialog(
            title=strings.SAVE_AS_FILE_LABEL,
            parent=self.get_ref(),
            action=Gtk.FileChooserAction.SAVE,
            action_button=Gtk.STOCK_SAVE,
            do_overwrite_confirmation=True,
            filters=self.__JSON_FILE_FILTERS,
        )

        self.strSessionFilename = fcd.get_filename()
        if self.strSessionFilename:
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
        def handle_destroy(*args):
            self.__help = None

        if self.__help:
            self.__help.present()
        else:
            if path.isfile("/usr/share/help/C/fapolicy-analyzer/User-Guide.html"):
                uri = "help:fapolicy-analyzer/User-Guide.html"
                logging.debug(f"loading help from {uri}")
            elif path.isfile("help/C/User-Guide.html"):
                # This should only happen in a development environment
                uri = f"file://{os.getcwd()}/help/C/User-Guide.html"
            else:
                uri = f"file://{os.getcwd()}/help/unavailable.html"
            self.__help = HelpBrowser(
                uri=uri,
                allow_navigation=False,
            )
            self.__help.connect("destroy", handle_destroy)
        self.__help.show()

    def resize_analysis_page(self, page):
        [height, width] = self.get_object("mainWindow").get_size()
        page.get_object("userDetailScroll").set_property(
            "height_request", int(height * Sizing.POLICY_BOTTOM_BOX)
        )
        page.get_object("subjectDetailScroll").set_property(
            "height_request", int(height * Sizing.POLICY_BOTTOM_BOX)
        )
        page.get_object("objectDetailScroll").set_property(
            "height_request", int(height * Sizing.POLICY_BOTTOM_BOX)
        )
        page.get_object("mainPane").set_position(
            int(width * Sizing.POLICY_OBJECT_WIDTH)
        )

    def on_syslogMenu_activate(self, *args):
        page = router(PAGE_SELECTION.ANALYZE_SYSLOG, "syslog")
        self.resize_analysis_page(page)
        self.__pack_main_content(page)

    def on_auditlogMenu_activate(self, *args):
        page = router(PAGE_SELECTION.ANALYZE_AUDIT, "audit")
        self.resize_analysis_page(page)
        self.__pack_main_content(page)

    def on_analyzeMenu_activate(self, *args):
        fcd = FileChooserDialog(
            title=strings.OPEN_FILE_LABEL,
            parent=self.get_ref(),
        )
        _file = fcd.get_filename() or ""

        if path.isfile(_file):
            page = router(PAGE_SELECTION.ANALYZE_FROM_DEBUG, "debug", _file)
            page.object_list.rule_view_activate += self.on_rulesAdminMenu_activate
            self.resize_analysis_page(page)
            self.__pack_main_content(page)

        fcd.destroy()

    def activate_file_analyzer(self, file):
        page = router(PAGE_SELECTION.ANALYZE_FROM_DEBUG, False, file)
        page.object_list.rule_view_activate += self.on_rulesAdminMenu_activate
        self.resize_analysis_page(page)
        self.__pack_main_content(page)

    def on_trustDbMenu_activate(self, menuitem, *args):
        self.__pack_main_content(router(PAGE_SELECTION.TRUST_DATABASE_ADMIN))

    def on_rulesAdminMenu_activate(self, *args, **kwargs):
        rulesPage = router(PAGE_SELECTION.RULES_ADMIN)
        if kwargs.get("rule_id", None) is not None:
            rulesPage.highlight_row_from_data(kwargs["rule_id"])
        self.__pack_main_content(rulesPage)

    def on_profileExecMenu_activate(self, *args):
        page = router(PAGE_SELECTION.PROFILER, self._fapd_mgr)
        page.analyze_button_pushed += self.activate_file_analyzer
        page.refresh_toolbar += self._refresh_toolbar
        self.__pack_main_content(page)

    def _refresh_toolbar(self):
        self.__toolbar.refresh_buttons_sensitivity()

    def on_deployChanges_clicked(self, *args):
        with DeployChangesetsOp(self.window) as op:
            op.run(self.__changesets, self.__system, self.__checkpoint)

    # ###################### fapolicyd interfacing ##########################
    def on_fapdStartMenu_activate(self, menuitem, data=None):
        logging.info("on_fapdStartMenu_activate() invoked.")
        if self._fapd_status != ServiceStatus.UNKNOWN:
            self._fapd_mgr.start()

    def on_fapdStopMenu_activate(self, menuitem, data=None):
        logging.info("on_fapdStopMenu_activate() invoked.")
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
                logging.warning("Daemon monitor query/update dispatch failed.")
            sleep(timeout)

    def _start_daemon_monitor(self):
        logging.info(f"start_daemon_monitor(): {self._fapd_status}")
        # Only start monitoring thread if fapolicyd is installed
        if self._fapd_status is not ServiceStatus.UNKNOWN:
            logging.info("Spawning monitor thread...")
            thread = Thread(target=self._monitor_daemon)
            thread.daemon = True
            thread.start()
            self._fapd_monitoring = True
            logging.debug(f"Thread={thread}, Running={self._fapd_monitoring}")
