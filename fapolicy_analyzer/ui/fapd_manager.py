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
import os
import subprocess


from datetime import datetime as DT
from enum import Enum
from fapolicy_analyzer import Handle
from threading import Lock
from time import time, sleep


class ServiceStatus(Enum):
    FALSE = False
    TRUE = True
    UNKNOWN = None


class FapdMode(Enum):
    DISABLED = 0
    ONLINE = 1
    PROFILING = 2


class FapdManager():
    def __init__(self, fapd_control_enabled=True):
        logging.debug("FapdManager::__init__(self)")
        self._current_instance = FapdMode.DISABLED
        self._previous_instance = FapdMode.DISABLED
        self._fapd_status = ServiceStatus.UNKNOWN
        self._fapd_monitoring = False
        self._fapd_ref = Handle("fapolicyd")
        self._fapd_profiler_pid = None

        # SU_OVERRIDE allows mode changes in development environment
        self._fapd_control_enabled = fapd_control_enabled
        self._fapd_control_override = os.environ.get("SU_OVERRIDE", False)

        self._fapd_lock = Lock()
        self.mode = FapdMode.DISABLED
        self.procProfile = None
        self._fapd_profiling_timestamp = None

        # Verify that fapolicyd is intalled, if so initialize fapd status
        self.initial_daemon_status()

        # ToDo: Verify that FAPD_LOGPATH works in the pkexec environment
        fapd_logpath_tmp = None
        fapd_logpath_tmp = os.environ.get("FAPD_LOGPATH")
        if fapd_logpath_tmp and len(fapd_logpath_tmp):
            self.fapd_profiling_stdout = fapd_logpath_tmp + ".stdout"
            self.fapd_profiling_stderr = fapd_logpath_tmp + ".stderr"
        else:
            self.fapd_profiling_stdout = None
            self.fapd_profiling_stderr = None

    def start(self, instance=FapdMode.ONLINE):
        # ToDo: Add logic to that online and profiling instances are mutex
        self.mode = instance
        self._start()

    def stop(self, instance=FapdMode.ONLINE):
        # ToDo: Add logic to that online and profiling instances are mutex
        self.mode = instance
        self._stop()

    def status(self, instance=FapdMode.ONLINE):
        # ToDo: Add logic to that online and profiling instances are mutex
        # ToDo: Consider returning a tuple with status and instance info
        self.mode = instance
        return self._status()

    def _start(self):
        logging.debug("FapdManager::start()")
        if self.mode == FapdMode.DISABLED:
            logging.debug("fapd is currently DISABLED")
            return False
        elif self.mode == FapdMode.ONLINE:
            logging.debug("fapd is initiating an ONLINE session")
            if (self._fapd_status != ServiceStatus.UNKNOWN) and (self._fapd_lock.acquire()):
                self._fapd_ref.start()
                self._fapd_lock.release()
        else:
            # PROFILING
            logging.debug("fapd is initiating a PROFILING session")
            logging.debug(f"Stdout: {self.fapd_profiling_stdout}")

            # If stdout path is not specified generate timestamped filename
            if not self.fapd_profiling_stdout:
                timeNow = DT.fromtimestamp(time())
                strTNow = timeNow.strftime("%Y%m%d_%H%M%S_%f")
                self._fapd_profiling_timestamp = strTNow

                stdoutPath = "/tmp/fapd_profiling_" + strTNow + ".stdout"
                stderrPath = "/tmp/fapd_profiling_" + strTNow + ".stderr"
                self.fapd_profiling_stdout = stdoutPath
                self.fapd_profiling_stderr = stderrPath

            fdStdoutPath = open(self.fapd_profiling_stdout, "w")
            fdStderrPath = open(self.fapd_profiling_stderr, "w")

            # ToDo: Move the following into a session object
            self.procProfile = subprocess.Popen(["/usr/sbin/fapolicyd",
                                                 "--permissive", "--debug"],
                                                stdout=fdStdoutPath,
                                                stderr=fdStderrPath)
            self._active_instance = FapdMode.PROFILING
            logging.debug(f"Fapd pid = {self.procProfile.pid}")

    def _stop(self):
        logging.debug("FapdManager::stop")
        if self.mode == FapdMode.DISABLED:
            logging.debug("fapd is currently DISABLED")
            return False
        elif self.mode == FapdMode.ONLINE:
            logging.debug("fapd is terminating an ONLINE session")
            if (self._fapd_status != ServiceStatus.UNKNOWN) and (self._fapd_lock.acquire()):
                self._fapd_ref.stop()
                self._fapd_lock.release()

        else:
            logging.debug("fapd is terminating a PROFILING session")
            self.procProfile.terminate()
            while self.procProfile.poll():
                sleep(1)
                logging.debug("Waiting for fapd profiling to shut down...")
            self.fapd_profiling_stderr = None
            self.fapd_profiling_stdout = None

    def _status(self):
        if self.mode == FapdMode.DISABLED:
            logging.debug("fapd is currently DISABLED")
            return ServiceStatus.UNKNOWN
        elif self.mode == FapdMode.ONLINE:
            try:
                if self._fapd_lock.acquire(blocking=False):
                    bStatus = ServiceStatus(self._fapd_ref.is_active())
                    if bStatus != self._fapd_status:
                        logging.debug(f"_status({bStatus} updated")
                        self._fapd_status = bStatus
                    self._fapd_lock.release()
            except Exception:
                print("Daemon monitor query/update dispatch failed.")
            return self._fapd_status
        else:
            logging.debug("fapd is in a PROFILING session")
            if self.procProfile:
                return ServiceStatus.TRUE
            else:
                return ServiceStatus.FALSE

    def initial_daemon_status(self):
        if self._fapd_lock.acquire():
            self._fapd_ref = Handle("fapolicyd")
            if self._fapd_ref.is_valid():
                self._fapd_status = ServiceStatus(self._fapd_ref.is_active())
            else:
                self._fapd_status = ServiceStatus.UNKNOWN
            self._fapd_lock.release()
