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
from enum import Enum
from locale import gettext as _
from os import getenv, geteuid, path
from threading import Lock, Thread
from time import sleep
from typing import Any

import fapolicy_analyzer.ui.strings as strings
import gi
from fapolicy_analyzer import Handle
from fapolicy_analyzer import __version__ as app_version
from fapolicy_analyzer.ui.ui_page import UIAction, UIPage
from fapolicy_analyzer.util.format import f

from .action_toolbar import ActionToolbar
from .actions import NotificationType, add_notification
from .analyzer_selection_dialog import ANALYZER_SELECTION
from .database_admin_page import DatabaseAdminPage
from .notification import Notification
from .operations import DeployChangesetsOp
from .policy_rules_admin_page import PolicyRulesAdminPage
from .rules import RulesAdminPage
from .session_manager import sessionManager
from .store import dispatch, get_system_feature
from .ui_widget import UIConnectedWidget
from .unapplied_changes_dialog import UnappliedChangesDialog

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib  # isort: skip


class ServiceStatus(Enum):
    FALSE = False
    TRUE = True
    UNKNOWN = None

class FapdMode(Enum):
    DISABLED = 0
    ONLINE = 1
    PROFILE = 2

class FapdManager():
    def __init__(self):
        logging.debug("FapdManager::__init__(self)")
        self.mode = FapdMode.DISABLED 
    

    def setMode(self, eMode):
        logging.debug("FapdManager::")
        self.mode = eMode

    def getMode(self):
        logging.debug("FapdManager::")
        return self.mode

    def start(self):
        logging.debug("FapdManager::")
        pass

    def stop(self):
        logging.debug("FapdManager::")
        pass

    # ###################### fapolicyd interfacing ##########################
    def on_fapdStart(self, menuitem, data=None):
        logging.debug("on_fapdStartMenu_activate() invoked.")
        if (self._fapd_status != ServiceStatus.UNKNOWN) and (self._fapd_lock.acquire()):
            self._fapd_ref.start()
            self._fapd_lock.release()

    def on_fapdStop(self, menuitem, data=None):
        logging.debug("on_fapdStopMenu_activate() invoked.")
        if (self._fapd_status != ServiceStatus.UNKNOWN) and (self._fapd_lock.acquire()):
            self._fapd_ref.stop()
            self._fapd_lock.release()

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
        logging.debug(f"__update_fapd_status({status})")

        # Enable/Disable fapd menu items
        self._enable_fapd_menu_items(status)
        if status is ServiceStatus.TRUE:
            self.fapdStatusLight.set_from_icon_name("emblem-default", size=4)
        elif status is ServiceStatus.FALSE:
            self.fapdStatusLight.set_from_icon_name("process-stop", size=4)
        else:
            self.fapdStatusLight.set_from_icon_name("edit-delete", size=4)

    def init_daemon(self):
        logging.debug("FapdManager::")
        if self._fapd_lock.acquire():
            self._fapd_ref = Handle("fapolicyd")
            if self._fapd_ref.is_valid():
                self._fapd_status = ServiceStatus(self._fapd_ref.is_active())
            else:
                self._fapd_status = ServiceStatus.UNKNOWN
            self.on_update_daemon_status(self._fapd_status)
            self._fapd_lock.release()

    def on_update_daemon_status(self, status: ServiceStatus):
        logging.debug("FapdManager::")
        logging.debug(f"on_update_daemon_status({status})")
        self._fapd_status = status
        GLib.idle_add(self._update_fapd_status, status)

    def _monitor_daemon(self, timeout=5):
        logging.debug("FapdManager::")
        logging.debug("_monitor_daemon() executing")
        while True:
            try:
                if self._fapd_lock.acquire(blocking=False):
                    bStatus = ServiceStatus(self._fapd_ref.is_active())
                    if bStatus != self._fapd_status:
                        logging.debug("monitor_daemon:Dispatch update request")
                        self.on_update_daemon_status(bStatus)
                    self._fapd_lock.release()
            except Exception:
                print("Daemon monitor query/update dispatch failed.")
            sleep(timeout)

    def _start_daemon_monitor(self):
        logging.debug("FapdManager::")
        logging.debug(f"start_daemon_monitor(): {self._fapd_status}")
        # Only start monitoring thread if fapolicy is installed
        if self._fapd_status is not ServiceStatus.UNKNOWN:
            logging.debug("Spawning monitor thread...")
            thread = Thread(target=self._monitor_daemon)
            thread.daemon = True
            thread.start()
            self._fapd_monitoring = True
            logging.debug(f"Thread={thread}, Running={self._fapd_monitoring}")
