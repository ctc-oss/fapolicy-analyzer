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
import subprocess
import time

from datetime import datetime as DT
from enum import Enum
from fapolicy_analyzer import Handle
from threading import Lock, Thread


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib


class ServiceStatus(Enum):
    FALSE = False
    TRUE = True
    UNKNOWN = None


class FapdMode(Enum):
    DISABLED = 0
    ONLINE = 1
    PROFILING = 2


class FapdManager():
    def __init__(self):
        logging.debug("FapdManager::__init__(self)")
        self._fapd_status = ServiceStatus.UNKNOWN
        self._fapd_monitoring = False
        self._fapd_ref = None
        self._fapd_profiler_pid = None
        self._fapd_lock = Lock()
        self.mode = FapdMode.DISABLED
        self.procProfile = None

    def set_mode(self, eMode):
        logging.debug(f"FapdManager::set_mode({eMode})")
        self.mode = eMode

    def get_mode(self):
        logging.debug("FapdManager::get_mode()")
        return self.mode

    def start(self):
        logging.debug("FapdManager::start()")
        if self.mode == FapdMode.DISABLED:
            logging.debug("fapd is currently DISABLED")
            return False
        elif self.mode == FapdMode.ONLINE:
            logging.debug("fapd is initiating an ONLINE session")
            subprocess.run(["echo", "Echoing starting an ONLINE session"])
            self.on_fapdStart(None)
        else:
            # PROFILING
            logging.debug("fapd is initiating a PROFILING session")

            timeNow = DT.fromtimestamp(time.time()).strftime("%Y%m%d_%H%M%S_%f")
            logDir = "/tmp/"
            stdoutPath = logDir + "fapd_profiling_" + timeNow + ".stdout"
            stderrPath = logDir + "fapd_profiling_" + timeNow + ".stderr"
            self.fapd_profiling_stdout = stdoutPath
            self.fapd_profiling_stderr = stderrPath
            fdStdoutPath = open(stdoutPath, "w")
            fdStderrPath = open(stderrPath, "w")

            # ToDo: Move the following into a session object
            self.procProfile = subprocess.Popen(["/usr/sbin/fapolicyd",
                                                 "--permissive", "--debug"],
                                                stdout=fdStdoutPath,
                                                stderr=fdStderrPath)
            print(self.procProfile.pid)

    def stop(self):
        logging.debug("FapdManager::stop")
        if self.mode == FapdMode.DISABLED:
            logging.debug("fapd is currently DISABLED")
            return False
        elif self.mode == FapdMode.ONLINE:
            logging.debug("fapd is terminating an ONLINE session")
            subprocess.Popen(["echo", "Echoing terminating an ONLINE session"])
            self.on_fapdStop(None)
        else:
            logging.debug("fapd is terminating a PROFILING session")
            self.procProfile.terminate()
            while self.procProfile.poll():
                time.sleep(1)
                logging.debug("Waiting for fapd profiling to shut down...")
            del self.procProfile
            self.procProfile = None

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
        logging.debug("FapdManager::init_daemon()")
        if self._fapd_lock.acquire():
            self._fapd_ref = Handle("fapolicyd")
            if self._fapd_ref.is_valid():
                self._fapd_status = ServiceStatus(self._fapd_ref.is_active())
            else:
                self._fapd_status = ServiceStatus.UNKNOWN
            self.on_update_daemon_status(self._fapd_status)
            self._fapd_lock.release()

    def on_update_daemon_status(self, status: ServiceStatus):
        logging.debug(f"FapdManager::on_update_daemon_status({status})")
        self._fapd_status = status
        GLib.idle_add(self._update_fapd_status, status)

    def _monitor_daemon(self, timeout=5):
        logging.debug("FapdManager::_monitor_daemon() executing")
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
            time.sleep(timeout)

    def _start_daemon_monitor(self):
        logging.debug(f"FapdManager::start_daemon_monitor():{self._fapd_status}")
        # Only start monitoring thread if fapolicy is installed
        if self._fapd_status is not ServiceStatus.UNKNOWN:
            logging.debug("Spawning monitor thread...")
            thread = Thread(target=self._monitor_daemon)
            thread.daemon = True
            thread.start()
            self._fapd_monitoring = True
            logging.debug(f"Thread={thread}, Running={self._fapd_monitoring}")
