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
import pwd
import re
import subprocess
import time
from .fapd_manager import FapdMode
from datetime import datetime as DT


def demote(user_uid, user_gid):
    def result():
        os.setgid(user_gid)
        os.setuid(user_uid)
    return result


class FaProfSession:
    def __init__(self, dictProfTgt, faprofiler=None):
        logging.debug(f"faProfSession::__init__({dictProfTgt}, {faprofiler})")
        self.execPath = dictProfTgt["executeText"]
        self.execArgs = dictProfTgt["argText"]
        self.listCmdLine = [self.execPath] + self.execArgs.split()
        self.user = dictProfTgt["userText"]
        self.pwd = dictProfTgt["dirText"]

        # Convert comma delimited string of "EnvVar=Value" substrings to dict
        self.env = {p[0]: re.sub(r'^"|"$', "", p[1])
                    for p in [s.split("=")
                              for s in [c.strip()
                                        for c in dictProfTgt["envText"].split(",")]]}
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

    def startTarget(self, instance_count, block_until_termination=True):
        logging.debug("FaProfSession::startTarget()")
        if not self.tgtStdout:
            self.timeStamp = self.get_profiling_timestamp()
            full_basename = f"/tmp/tgt_profiling_{self.timeStamp}_{self.name}"
            self.tgtStdout = f"{full_basename}_{instance_count}.stdout"
            self.tgtStderr = f"{full_basename}_{instance_count}.stderr"
        fdTgtStdout = open(self.tgtStdout, "w")
        fdTgtStderr = open(self.tgtStderr, "w")

        # Convert username to uid/gid
        pw_record = pwd.getpwnam(self.user)
        # homedir = pw_record.pw_dir
        uid = pw_record.pw_uid
        gid = pw_record.pw_gid

        # Capture process object
        # Does this block? Are there options to select blocking/nonblocking?
        logging.debug(f"Starting {self.listCmdLine} as {uid}/{gid}")
        logging.debug(f"in {self.pwd} with env: {self.env}")
        self.procTarget = subprocess.Popen(self.listCmdLine,
                                           stdout=fdTgtStdout,
                                           stderr=fdTgtStderr,
                                           cwd=self.pwd,
                                           env=self.env,
                                           preexec_fn=demote(uid, gid)
                                           )
        logging.debug(self.procTarget.pid)

        # Block until process terminates
        if block_until_termination:
            logging.debug("Waiting for profiling target to terminate...")
            self.procTarget.wait()
            # del self.procTarget
            self.procTarget = None
        return self.procTarget

    def stopTarget(self):
        """
        Terminate the profiling target and the associated profiling session
        """
        if self.procTarget:
            self.procTarget.terminate()
            self.procTarget.wait()
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
    def __init__(self, fapd_mgr=None, fapd_persistance=True):
        logging.debug("FaProfiler::__init__()")
        self.fapd_mgr = fapd_mgr
        self.fapd_persistance = fapd_persistance
        self.fapd_pid = None
        self.strTimestamp = None
        self.strExecPath = None
        self.strExecArgs = None
        self.dictFaProfSession = dict()  # dict of current / completed sessions
        self.instance = 0

    def start_prof_session(self, dictArgs, block_until_term=True):
        """
        Invoke target executable.
        self.dictFaProfSession is a dict of current tgt profiling sessions
        associated with a single fapd profiling instance
        """
        logging.debug(f"FaProfiler::start_prof_session('{dictArgs}')")
        self.fapd_mgr.start(FapdMode.PROFILING)
        if self.fapd_mgr.procProfile:
            self.fapd_pid = self.fapd_mgr.procProfile.pid

        time.sleep(10)
        self.faprofSession = FaProfSession(dictArgs, self)
        key = str(self.instance) + "-" + dictArgs["executeText"]
        self.dictFaProfSession[key] = self.faprofSession
        self.faprofSession.startTarget(self.instance, block_until_term)
        if not self.fapd_persistance:
            self.fapd_mgr.stop(FapdMode.PROFILING)
            self.fapd_pid = None
        else:
            self.instance += 1
        return key

    def status_prof_session(self, sessionName=None):
        logging.debug("FaProfiler::status_prof_session()")
        return self.dictFaProfSession[sessionName].get_status()

    def stop_prof_session(self, sessionName=None):
        logging.debug("FaProfiler::stop_prof_session()")
        self.fapd_mgr.stop(FapdMode.PROFILING)
        if sessionName:
            self.dictFaProfSession[sessionName].stopTarget()
            del self.dictFaProfSession[sessionName]
        else:
            for k in self.dictFaProfSession.keys():
                logging.debug(f"Stopping profiling session: {k}")
                self.dictFaProfSession[k].stopTarget()
                del self.dictFaProfSession[k]
        self.instance = 0

    def get_profiling_timestamp(self):
        if self.fapd_mgr:
            self.strTimestamp = self.fapd_mgr._fapd_profiling_timestamp
        return self.strTimestamp
