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


class FaProfSession:
    def __init__(self, dictProfTgt, fapd_mgr=None):
        logging.debug(f"faProfSession::__init__({dictProfTgt}, {fapd_mgr})")
        self.execPath = dictProfTgt["executeText"]
        self.execArgs = dictProfTgt["argText"]
        self.listCmdLine = [self.execPath] + self.execArgs.split()
        self.user = dictProfTgt["userText"]
        self.pwd = dictProfTgt["dirText"]
        self.env = dictProfTgt["envText"]
        self.fapd_mgr = fapd_mgr
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

    def startTarget(self):
        logging.debug("FaProfSession::startTarget()")
        if not self.tgtStdout:
            self.timeStamp = self.fapd_mgr.get_profiling_timestamp()
            self.tgtStdout = f"/tmp/tgt_profiling_{self.timeStamp}_{self.name}.stdout"
            self.tgtStderr = f"/tmp/tgt_profiling_{self.timeStamp}_{self.name}.stderr"
        fdTgtStdout = open(self.tgtStdout, "w")
        fdTgtStderr = open(self.tgtStderr, "w")

        # Capture process object
        self.procTarget = subprocess.Popen(self.listCmdLine,
                                           stdout=fdTgtStdout,
                                           stderr=fdTgtStderr)
        print(self.procTarget.pid)

        # Block until process terminates
        while self.procTarget.poll():
            time.sleep(1)
            logging.debug("Waiting for profiling target to terminate...")
        del self.procTarget
        self.procTarget = None

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
        self.strExecPath = None
        self.strExecArgs = None
        self.listFaProfSession = dict()  # dict of current / completed sessions

    def start_prof_session(self, strCommandLine):
        logging.debug(f"FaProfiler::start_prof_session('{strCommandLine}')")
        self.faprofSession = FaProfSession(strCommandLine, self.fapd_mgr)
        self.listFaProfSession[strCommandLine["executeText"]] = self.faprofSession
        bResult = self.faprofSession.startTarget()
        return bResult

    def status_prof_session(self, sessionName):
        logging.debug("FaProfiler::status_prof_session()")
        return self.listFaProfSession[sessionName].get_status()

    def terminate_prof_session(self, sessionName):
        logging.debug("FaProfiler::terminate_prof_session()")
        self.listFaProfSession[sessionName].clean_all()
