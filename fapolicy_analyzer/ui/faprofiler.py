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
    def __init__(self, strCmdLine):
        self.listCmdLine = strCmdLine.split()
        logging.debug(f"faProfSession::__init__({self.listCmdLine})")
        self.strName = os.path.basename(self.listCmdLine[0])
        self.strTimeStart = None
        self.strStdoutPath = None
        self.strStdErrPath = None
        self.strExecPath = self.listCmdLine[0]
        self.strExecArgs = self.listCmdLine[1:]
        self.strStatus = None  # Queued, InProgress, Complete (?)
        self.procTarget = None

    def startTarget(self):
        logDir = "/tmp/"
        self.stdoutPath = logDir + "fapd_profiling_" + self.strName + ".stdout"
        self.stderrPath = logDir + "fapd_profiling_" + self.strName + ".stderr"
        fdStdoutPath = open(self.stdoutPath, "w")
        fdStderrPath = open(self.stderrPath, "w")

        # Capture process object
        self.procTarget = subprocess.Popen(self.listCmdLine,
                                           stdout=fdStdoutPath,
                                           stderr=fdStderrPath)
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
    def __init__(self):
        logging.debug("FaProfiler::__init__()")
        self.strExecPath = None
        self.strExecArgs = None
        self.listFaProfSession = dict()  # dict of current / completed sessions

    def start_prof_session(self, strCommandLine):
        logging.debug(f"FaProfiler::start_prof_session('{strCommandLine}')")
        self.faprofSession = FaProfSession(strCommandLine)
        self.listFaProfSession[strCommandLine] = self.faprofSession
        bResult = self.faprofSession.startTarget()
        return bResult

    def status_prof_session(self, sessionName):
        logging.debug("FaProfiler::status_prof_session()")
        return self.listFaProfSession[sessionName].get_status()

    def terminate_prof_session(self, sessionName):
        logging.debug("FaProfiler::terminate_prof_session()")
        self.listFaProfSession[sessionName].clean_all()
