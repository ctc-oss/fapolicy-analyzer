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
    def __init__(self, bSuFapdControl=True):
        logging.debug("FapdManager::__init__(self)")
        self._fapd_status = ServiceStatus.UNKNOWN
        self._fapd_monitoring = False
        self._fapd_ref = Handle("fapolicyd")
        self._fapd_profiler_pid = None
        self._fapd_control_enabled = bSuFapdControl
        self._fapd_lock = Lock()
        self.mode = FapdMode.DISABLED
        self.procProfile = None

        # Verify that fapolicyd is intalled, if so initialize fapd status
        self.initial_daemon_status()

        if os.environ.get("FAPD_LOGPATH"):
            self.fapd_profiling_stdout = os.environ.get("FAPD_LOGPATH") + ".stdout"
            self.fapd_profiling_stderr = os.environ.get("FAPD_LOGPATH") + ".stderr"
        else:
            self.fapd_profiling_stdout = None
            self.fapd_profiling_stderr = None
        self._fapd_profiling_timestamp = None

    def set_profiling_stdout(self, strStdoutPath):
        logging.debug("FapdManager::set_profiling_stdout()")
        self.fapd_profiling_stdout = strStdoutPath
        return self.fapd_profiling_stdout

    def set_profiling_stderr(self, strStderrPath):
        logging.debug("FapdManager::set_profiling_stderr()")
        self.fapd_profiling_stderr = strStderrPath
        return self.fapd_profiling_stderr

    def get_profiling_stdout(self):
        logging.debug("FapdManager::get_profiling_stdout()")
        return self.fapd_profiling_stdout

    def get_profiling_stderr(self):
        logging.debug("FapdManager::get_profiling_stderr()")
        return self.fapd_profiling_stderr

    def set_mode(self, eMode):
        """Allow only su to modify the instance mode"""
        logging.debug(f"FapdManager::set_mode({eMode})")
        if self._fapd_control_enabled:
            self.mode = eMode

    def get_mode(self):
        logging.debug("FapdManager::get_mode()")
        return self.mode

    def get_profiling_timestamp(self):
        logging.debug("FapdManager::get_profiling_timestamp()")
        return self._fapd_profiling_timestamp

    def start(self):
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
            logging.debug(f"Fapd pid = {self.procProfile.pid}")

    def stop(self):
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

    def status_online(self):
        try:
            if self._fapd_lock.acquire(blocking=False):
                bStatus = ServiceStatus(self._fapd_ref.is_active())
                logging.debug(f"status_online() -> {bStatus}")
                if bStatus != self._fapd_status:
                    logging.debug(f"status_online({bStatus} updated")
                    self._fapd_status = bStatus
                self._fapd_lock.release()
        except Exception:
            print("Daemon monitor query/update dispatch failed.")
        logging.debug(f"FapdManager::status_online()::{self._fapd_status})")
        return self._fapd_status

    def initial_daemon_status(self):
        if self._fapd_lock.acquire():
            self._fapd_ref = Handle("fapolicyd")
            if self._fapd_ref.is_valid():
                self._fapd_status = ServiceStatus(self._fapd_ref.is_active())
            else:
                self._fapd_status = ServiceStatus.UNKNOWN
            self._fapd_lock.release()
