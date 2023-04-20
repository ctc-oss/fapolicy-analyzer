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
import sys
import subprocess


from datetime import datetime as DT
from enum import Enum
from fapolicy_analyzer import Handle
from fapolicy_analyzer.ui.actions import (NotificationType, add_notification)
from fapolicy_analyzer.ui.store import dispatch
from fapolicy_analyzer.ui.strings import (FAPD_DBUS_STOP_ERROR_MSG,
                                          FAPD_DBUS_START_ERROR_MSG)
from threading import Lock
from time import time, sleep


class ServiceStatus(Enum):
    FALSE = False
    TRUE = True
    UNKNOWN = None


class FapdMode(Enum):
    DISABLED = 0  # Neither fapd instance is executing
    ONLINE = 1
    PROFILING = 2


def _promote():
    def result():
        os.setgid(0)
        os.setuid(0)
    return result


class FapdManager():
    def __init__(self, fapd_control_enabled=True):
        logging.info(f"FapdManager constructed, control:{fapd_control_enabled}")

        # What fapd instances are available (if any)
        self._current_instance = FapdMode.DISABLED
        self._previous_instance = FapdMode.DISABLED

        # What fapd instances are active currently
        self._fapd_status = ServiceStatus.UNKNOWN
        self._fapd_profiling_status = ServiceStatus.UNKNOWN

        # fapd manager state is used to return to prior state after profiling
        self._fapd_cur_online_state = ServiceStatus.UNKNOWN
        self._fapd_prior_online_state = ServiceStatus.UNKNOWN

        # Run thread to peroidically poll online fapd status
        self._fapd_monitoring = False
        self._fapd_ref = Handle("fapolicyd")

        # Verify that fapolicyd is installed, if so initialize fapd status
        self._fapd_lock = Lock()
        self.mode = FapdMode.DISABLED
        self.initial_daemon_status()

        # Initialize fapd profiling instance vars
        self._fapd_profiler_pid = None
        self.procProfile = None
        self._fapd_profiling_timestamp = None

        # SU_OVERRIDE allows mode changes in development environment
        self._fapd_control_enabled = fapd_control_enabled
        self._fapd_control_override = os.environ.get("SU_OVERRIDE", False)

        # ToDo: Verify that FAPD_LOGPATH works in the pkexec environment
        fapd_logpath_tmp = os.environ.get("FAPD_LOGPATH")
        if fapd_logpath_tmp:
            logging.debug(f"FapdManager.__init__() logpath:{fapd_logpath_tmp}")
            self.fapd_profiling_stdout = fapd_logpath_tmp + ".stdout"
            self.fapd_profiling_stderr = fapd_logpath_tmp + ".stderr"
        else:
            self.fapd_profiling_stdout = None
            self.fapd_profiling_stderr = None

    def start(self, instance=FapdMode.ONLINE):
        # If profiling, get current fapd state, and stop it if running
        if instance == FapdMode.PROFILING:
            self.capture_online_state()
            self._stop()

        # On-line, so check status of fapd profiling instance and bring it down
        elif self._fapd_profiling_status:
            logging.debug("FapdManager::start(): Shutting down prof fapd")
            self._stop(FapdMode.PROFILING)

        pid = self._start(instance)
        return pid

    def stop(self, instance=FapdMode.ONLINE):
        self._stop(instance)
        # Revert on-line fapd state
        if instance == FapdMode.PROFILING:
            self.revert_online_state()

    def status(self, instance=FapdMode.ONLINE):
        # ToDo: Add logic to that online and profiling instances are mutex
        # ToDo: Consider returning a tuple with status and instance info
        self.mode = instance
        return self._status()

    def _start(self, instance=FapdMode.ONLINE):
        logging.info("FapdManager::_start()")

        # Generate timestamp for any new fapd session whether it's used or not
        timeNow = DT.fromtimestamp(time())
        strTNow = timeNow.strftime("%Y%m%d_%H%M%S_%f")
        self._fapd_profiling_timestamp = strTNow

        if self.mode == FapdMode.DISABLED:
            logging.warning("fapd is currently DISABLED")
            return None

        # Verify user permission to start/stop an fapd instance
        if not self._fapd_control_enabled and not self._fapd_control_override:
            logging.warning("FapdManager::_start()::root permissions required")
            return None

        if instance == FapdMode.ONLINE:
            logging.debug("fapd is initiating an ONLINE session")
            if (self._fapd_status != ServiceStatus.UNKNOWN):
                try:
                    with self._fapd_lock:
                        self._fapd_ref.start()
                        self.mode = FapdMode.ONLINE

                except Exception:
                    self._fapd_status = ServiceStatus.UNKNOWN
                    logging.error(FAPD_DBUS_START_ERROR_MSG)
                    dispatch(add_notification(FAPD_DBUS_START_ERROR_MSG,
                                              NotificationType.ERROR))

        else:
            # PROFILING
            logging.debug("fapd is initiating a PROFILING session")
            logging.debug(f"Stdout: {self.fapd_profiling_stdout}")

            # If stdout path is not specified generate timestamped filename
            if not self.fapd_profiling_stdout:
                stdoutPath = "/tmp/fapd_profiling_" + strTNow + ".stdout"
                stderrPath = "/tmp/fapd_profiling_" + strTNow + ".stderr"
                self.fapd_profiling_stdout = stdoutPath
                self.fapd_profiling_stderr = stderrPath

            fdStdoutPath = open(self.fapd_profiling_stdout, "w")
            fdStderrPath = open(self.fapd_profiling_stderr, "w")

            if self._fapd_status:
                logging.debug("FapdManager::_start() - Shut down online fapd")
                self._previous_instance = self._fapd_status
                self._stop(FapdMode.ONLINE)

            self.procProfile = subprocess.Popen(["/usr/sbin/fapolicyd",
                                                 "--permissive",
                                                 "--debug",
                                                 "--no-details"],
                                                stdout=fdStdoutPath,
                                                stderr=fdStderrPath,
                                                preexec_fn=_promote()
                                                )
            self._active_instance = FapdMode.PROFILING
            self._fapd_profiler_pid = self.procProfile.pid
            self.mode = FapdMode.PROFILING
            logging.debug(f"Fapd pid = {self._fapd_profiler_pid}")

            # Magic delay value for profiling instance to complete init
            # Consider active polling/monitoring here. fapd must be fully up
            # prior to invoking profiling executable target.
            sleep(10)
            return self.procProfile

    def _stop(self, instance=FapdMode.ONLINE):
        logging.info(f"FapdManager::_stop({instance})")
        if self.mode == FapdMode.DISABLED:
            logging.warning("fapd is currently DISABLED")
            return False

        # Verify user permissions to start/stop an fapd instance
        if not self._fapd_control_enabled and not self._fapd_control_override:
            logging.warning("FapdManager::_stop()::root permissions required")
            return False

        if instance == FapdMode.ONLINE:
            logging.debug("fapd is terminating an ONLINE session")
            if (self._fapd_status != ServiceStatus.UNKNOWN):
                try:
                    with self._fapd_lock:
                        self._fapd_ref.stop()

                except Exception:
                    logging.error(FAPD_DBUS_STOP_ERROR_MSG)
                    dispatch(add_notification(FAPD_DBUS_STOP_ERROR_MSG,
                                              NotificationType.ERROR))

        else:
            logging.debug("fapd is terminating a PROFILING session")
            logging.debug(f"self.procProfile = {self.procProfile}")
            if self.procProfile:
                logging.debug(f"Pid: {self.procProfile.pid}")
                self.procProfile.terminate()
                self.procProfile.wait(5)
            self.fapd_profiling_stderr = None
            self.fapd_profiling_stdout = None
            self._fapd_profiler_pid = None

    def _status(self):
        if self.mode == FapdMode.DISABLED:
            logging.debug("fapd is currently DISABLED")
            return ServiceStatus.UNKNOWN
        elif self.mode == FapdMode.ONLINE:
            if self._fapd_lock.acquire(blocking=False):
                try:
                    bStatus = ServiceStatus(self._fapd_ref.is_active()) if self._fapd_ref.is_valid()) else ServiceStatus(None)
                    if bStatus != self._fapd_status:
                        logging.debug(f"_status({bStatus} updated")
                        self._fapd_status = bStatus
                except Exception:
                    logging.warning("Daemon status query/update failed.")

                self._fapd_lock.release()
            return self._fapd_status
        else:
            logging.debug("fapd is in a PROFILING session")
            if self.procProfile:
                return ServiceStatus.TRUE
            else:
                return ServiceStatus.FALSE

    def capture_online_state(self):
        logging.debug("capture_online_state(): Capturing current online status")
        with self._fapd_lock:
            try:
                updated_online_state = ServiceStatus(self._fapd_ref.is_active())
                self._fapd_prior_online_state = updated_online_state
                self._fapd_cur_online_state = updated_online_state
            except Exception:
                logging.warning("Daemon online status query/update failed.")

        logging.debug(f"prior_online_state = {self._fapd_prior_online_state}")

    def revert_online_state(self):
        logging.info("revert_online_state()")
        logging.debug(f"Reverting to {self._fapd_prior_online_state}")
        if self._fapd_prior_online_state == ServiceStatus.TRUE:
            self._start(FapdMode.ONLINE)

    def initial_daemon_status(self):
        with self._fapd_lock:
            try:
                if self._fapd_ref.is_valid():
                    self._fapd_status = ServiceStatus(self._fapd_ref.is_active())
                else:
                    self._fapd_status = ServiceStatus.UNKNOWN
            except Exception as e:
                print(f"Fapd Handle is_valid() or is_active() exception: {e}",
                      file=sys.stderr)
                raise
