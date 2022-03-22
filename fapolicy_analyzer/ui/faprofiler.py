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


class FaProfSession:
    def __init__(self, strExecPath):
        self.strName = os.path.basename(strExecPath)
        self.strTimeStart = None
        self.strStdoutPath = None
        self.strStdErrPath = None
        self.strExecPath = strExecPath
        self.strExecArgs = None
        self.strStatus = None  # Queued, InProgress, Complete (?)

    def get_status(self):
        logging.debug("FaProfSession::get_status()")
        return self.strStatus

    def clean_all(self):
        logging.debug("FaProfSession::clean_all()")
        # Delete all log file artifacts
        pass


class FaProfiler:
    def __init__(self):
        self.strExecPath = None
        self.strExecArgs = None
        self.listFaProfSession = dict()  # dict of current / completed sessions

    def start_prof_session(self, strTarget, listArgs):
        logging.debug("FaProfiler::start_prof_session()")
        self.faprofSession = FaProfSession(strTarget)
        self.listFaProfSession[strTarget] = self.faprofSession
        self.strName
        return self.strName

    def status_prof_session(self, sessionName):
        logging.debug("FaProfiler::status_prof_session()")
        return self.listFaProfSession[sessionName].get_status()

    def terminate_prof_session(self, sessionName):
        logging.debug("FaProfiler::terminate_prof_session()")
        self.listFaProfSession[sessionName].clean_all()
