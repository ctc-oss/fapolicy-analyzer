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
import os.path
import subprocess
import time
from .fapd_manager import FapdMode
from datetime import datetime as DT


class FaProfSession:
    def __init__(self, dictProfTgt, faprofiler=None):
        logging.debug(f"faProfSession::__init__({dictProfTgt}, {faprofiler})")
        self.execPath = dictProfTgt["executeText"]
        self.execArgs = dictProfTgt["argText"]
        self.listCmdLine = [self.execPath] + self.execArgs.split()
        self.user = dictProfTgt["userText"]
        self.pwd = dictProfTgt["dirText"]
        self.env = dictProfTgt["envText"]
        self.faprofiler = faprofiler
        self.name = os.path.basename(self.execPath)
        self.timeStamp = None
        self.status = None  # Queued, InProgress, Complete (?)
        self.procTarget = None

        # Temp demo workaround for setting target log file paths
        if os.environ.get("FAPD_LOGPATH"):
            self.tgtStdout = os.environ.get("FAPD_LOGPATH") + f"_{self.name}.stdout"
            self.tgtStderr = os.environ.get("FAPD_LOGPATH") + f"_{self.name}.stderr"
        else:
            self.tgtStdout = None
            self.tgtStderr = None

    def startTarget(self, block_until_termination=True):
        logging.debug("FaProfSession::startTarget()")
        if not self.tgtStdout:
            self.timeStamp = self.get_profiling_timestamp()
            self.tgtStdout = f"/tmp/tgt_profiling_{self.timeStamp}_{self.name}.stdout"
            self.tgtStderr = f"/tmp/tgt_profiling_{self.timeStamp}_{self.name}.stderr"
        fdTgtStdout = open(self.tgtStdout, "w")
        fdTgtStderr = open(self.tgtStderr, "w")

        # Capture process object
        # Does this block? Are there options to select blocking/nonblocking?
        self.procTarget = subprocess.Popen(self.listCmdLine,
                                           stdout=fdTgtStdout,
                                           stderr=fdTgtStderr)
        logging.debug(self.procTarget.pid)

        # Block until process terminates
        if block_until_termination:
            while self.procTarget.poll():
                time.sleep(1)
                logging.debug("Waiting for profiling target to terminate...")
            del self.procTarget
            self.procTarget = None

    def stopTarget(self):
        """
        Terminate the profiling target and the associated profiling session
        """
        if self.procTarget:
            # tbd how we'll terminate the target - self.procTarget.terminate()
            while self.procTarget.poll():
                time.sleep(1)
                logging.debug("Waiting for profiling target to terminate...")
            del self.procTarget
            self.procTarget = None

    def get_profiling_timestamp(self):
        """
        Timestamp used in session logfile names is associated with the
        current fapd profiling instance
        """
        if self.faprofiler:
            self.timeStamp = self.faprofiler.get_profiling_timestamp()

        if not self.timeStamp:
            timeNow = DT.fromtimestamp(time.time())
            self.timeStamp = timeNow.strftime("%Y%m%d_%H%M%S_%f")

        return self.timeStamp

    def get_status(self):
        logging.debug("FaProfSession::get_status()")
        return self.strStatus

    def clean_all(self):
        logging.debug("FaProfSession::clean_all()")
        # Delete all log file artifacts
        pass


class FaProfiler:
    def __init__(self, fapd_mgr=None):
        logging.debug("FaProfiler::__init__()")
        self.fapd_mgr = fapd_mgr
        self.strTimestamp = None
        self.strExecPath = None
        self.strExecArgs = None
        self.listFaProfSession = dict()  # dict of current / completed sessions

    def start_prof_session(self, dictArgs):
        """
        Invoke target executable.
        This is still a work in progress. I want to keep a dict of current
        tgt profiling session associated with a single fapd profiling
        session.
        """
        logging.debug(f"FaProfiler::start_prof_session('{dictArgs}')")
        self.fapd_mgr.start(FapdMode.PROFILING)
        self.faprofSession = FaProfSession(dictArgs, self)
        self.listFaProfSession[dictArgs["executeText"]] = self.faprofSession
        bResult = self.faprofSession.startTarget()
        return bResult

    def status_prof_session(self, sessionName=None):
        logging.debug("FaProfiler::status_prof_session()")
        return self.listFaProfSession[sessionName].get_status()

    def stop_prof_session(self, sessionName=None):
        logging.debug("FaProfiler::stop_prof_session()")
        self.fapd_mgr.stop(FapdMode.PROFILING)
        if sessionName:
            self.listFaProfSession[sessionName].clean_all()

    def get_profiling_timestamp(self):
        if self.fapd_mgr:
            self.strTimestamp = self.fapd_mgr._fapd_profiling_timestamp
        return self.strTimestamp
