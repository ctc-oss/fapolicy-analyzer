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
import subprocess
import shutil
import time
from fapolicy_analyzer.ui.actions import NotificationType, add_notification
from fapolicy_analyzer.ui.fapd_manager import FapdMode
from fapolicy_analyzer.ui.store import dispatch
from datetime import datetime as DT
from enum import Enum

import fapolicy_analyzer.ui.strings as s


class ProfSessionStatus(Enum):
    QUEUED = 0
    INPROGRESS = 1
    COMPLETED = 2


class ProfSessionArgsStatus(Enum):
    OK = 0
    EXEC_EMPTY = 1
    EXEC_DOESNT_EXIST = 2
    EXEC_NOT_EXEC = 3
    USER_DOESNT_EXIST = 4
    PWD_DOESNT_EXIST = 5
    PWD_ISNT_DIR = 6
    UNKNOWN = 7


def EnumErrorPairs2Str(dictStatusEnums):
    return "\n  ".join([f"Error: {r}" for r in (dictStatusEnums or {}).values()])


class ProfSessionException(RuntimeError):
    def __init__(self, msg="Unknown error",
                 enumError=ProfSessionArgsStatus.UNKNOWN):
        self.error_msg = f"Profiler Session: {msg}"
        self.error_enum = enumError


class FaProfSession:
    def __init__(self, dictProfTgt, faprofiler=None):
        logging.debug(f"faProfSession::__init__({dictProfTgt}, {faprofiler})")
        self.throwOnInvalidSessionArgs(dictProfTgt)

        # Executable command and arguments
        self.execPath = dictProfTgt["executeText"]
        self.execArgs = dictProfTgt["argText"]
        self.listCmdLine = [self.execPath] + self.execArgs.split()

        # euid, working directory and environment variables
        self.user = dictProfTgt["userText"]
        self.pwd = dictProfTgt["dirText"]

        # Convert comma delimited string of "EnvVar=Value" substrings to dict
        self.env = FaProfSession._comma_delimited_kv_string_to_dict(
            dictProfTgt["envText"]
        )

        self.faprofiler = faprofiler
        self.name = os.path.basename(self.execPath)
        self.timeStamp = None
        self.status = ProfSessionStatus.QUEUED
        self.procTarget = None

        # Temp demo workaround for setting target log file paths
        if os.environ.get("FAPD_LOGPATH"):
            self.tgtStdout = os.environ.get("FAPD_LOGPATH") + f"_{self.name}.stdout"
            self.tgtStderr = os.environ.get("FAPD_LOGPATH") + f"_{self.name}.stderr"
        else:
            self.tgtStdout = None
            self.tgtStderr = None

        # File descriptors are state variables; closed in stopTarget()
        self.fdTgtStdout = None
        self.fdTgtStderr = None

    def startTarget(self, instance_count, block_until_termination=True):
        logging.debug("FaProfSession::startTarget()")

        if not self.tgtStdout:
            self.timeStamp = self.get_profiling_timestamp()
            full_basename = f"/tmp/tgt_profiling_{self.timeStamp}_{self.name}"
            self.tgtStdout = f"{full_basename}_{instance_count}.stdout"
            self.tgtStderr = f"{full_basename}_{instance_count}.stderr"

        try:
            self.fdTgtStdout = open(self.tgtStdout, "w")
            self.fdTgtStderr = open(self.tgtStderr, "w")
        except Exception as e:
            logging.warning(f"{s.FAPROFILER_TGT_REDIRECTION_ERROR_MSG}: {e}")
            dispatch(
                add_notification(
                    s.FAPROFILER_TGT_REDIRECTION_ERROR_MSG + f": {e}",
                    NotificationType.ERROR,
                )
            )

            self.fdTgtStdout = None
            self.fdTgtStderr = None

        # Set pwd - Use current dir for pwd if not supplied by user
        working_dir = self.pwd if self.pwd else os.getcwd()

        # Convert username to uid/gid
        u_valid = False
        try:
            if self.user:
                # Get uid/gid of new user and the associated default group
                pw_record = pwd.getpwnam(self.user)
                uid = pw_record.pw_uid
                gid = pw_record.pw_gid
                logging.debug(f"The uid/gid of the profiling tgt: {uid}/{gid}")

                # Change the ownership of profiling tgt's stdout and stderr
                logging.debug(
                    f"Changing ownership of fds: {self.fdTgtStdout},{self.fdTgtStderr}"
                )
                os.fchown(self.fdTgtStdout.fileno(), uid, gid)
                os.fchown(self.fdTgtStderr.fileno(), uid, gid)
                logging.debug(
                    f"Changed the profiling tgt stdout/err ownership {uid},{gid}"
                )
                u_valid = True
            else:
                # In production, the following will be the superuser defaults
                uid = os.getuid()
                gid = os.getgid()

        except Exception as e:
            # Use current uid/gid if getpwnam() or chown throws an exception by
            # setting prexec_fn = None
            # Typically will only occur in debug/development runs

            logging.error(f"{s.FAPROFILER_TGT_EUID_CHOWN_ERROR_MSG}: {e}")
            dispatch(
                add_notification(
                    s.FAPROFILER_TGT_EUID_CHOWN_ERROR_MSG + f": {e}",
                    NotificationType.ERROR,
                )
            )

            uid = os.getuid()  # Place holder args to _demote()
            gid = os.getgid()

        # Capture process object
        try:
            logging.debug(f"Starting {self.listCmdLine} as {uid}/{gid}")
            logging.debug(f"in {self.pwd} with env: {self.env}")
            self.procTarget = subprocess.Popen(
                self.listCmdLine,
                stdout=self.fdTgtStdout,
                stderr=self.fdTgtStderr,
                cwd=working_dir,
                env=self.env,
                preexec_fn=FaProfSession._demote(u_valid, uid, gid),
            )
            logging.debug(self.procTarget.pid)
            self.status = ProfSessionStatus.INPROGRESS

            # Block until process terminates
            if block_until_termination:
                logging.debug("Waiting for profiling target to terminate...")
                self.procTarget.wait()
                self.status = ProfSessionStatus.COMPLETED

        except Exception as e:
            logging.error(f"Profiling target Popen failure: {e}")
            dispatch(
                add_notification(
                    s.FAPROFILER_TGT_POPEN_ERROR_MSG + f": {e}",
                    NotificationType.ERROR,
                )
            )
        return self.procTarget

    def stopTarget(self):
        """
        Terminate the profiling target and the associated profiling session
        """
        if self.procTarget:
            self.procTarget.terminate()
            self.procTarget.wait()
            self.status = ProfSessionStatus.COMPLETED

        if self.fdTgtStdout:
            self.fdTgtStdout.close()

        if self.fdTgtStderr:
            self.fdTgtStderr.close()

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

        # Poll the Popen object if it exists, poll() returns None if running
        if self.procTarget:
            if self.procTarget.poll() is None:
                self.status = ProfSessionStatus.INPROGRESS
            else:
                self.status = ProfSessionStatus.COMPLETED
        else:
            self.status = ProfSessionStatus.QUEUED
        return self.status

    def clean_all(self):
        logging.debug("FaProfSession::clean_all()")
        # Delete all log file artifacts

    @staticmethod
    def _rel_tgt_which(relative_exec, user_provided_env):
        """
        Given a specified relative executable and a colon separated PATH string
        or the environment PATH variable return the absolute path to
        the executable
        """
        # If exec_path is relative use user provided PATH or else env var PATH
        if user_provided_env and "PATH" in user_provided_env:
            search_path = user_provided_env.get("PATH")
        else:
            search_path = os.getenv("PATH")
        logging.debug(f"Profiling PATH = {search_path}")

        return shutil.which(relative_exec, path=search_path)

    @staticmethod
    def validSessionArgs(dictProfTgt):
        """Determine Profiler session argument status. Return bool"""
        return ProfSessionArgsStatus.OK in FaProfSession.validateArgs(dictProfTgt)

    @staticmethod
    def throwOnInvalidSessionArgs(dictProfTgt):
        """Throw exception on first invalid Profiler session argument."""
        dictInvalidEnums = FaProfSession.validateArgs(dictProfTgt)
        if ProfSessionArgsStatus.OK not in dictInvalidEnums:
            error_enum = next(iter(dictInvalidEnums))
            error_msg = dictInvalidEnums[error_enum]
            raise ProfSessionException(error_msg, error_enum)

    @staticmethod
    def validateArgs(dictProfTgt):
        """
        Validates the Profiler Session object's user, target, pwd parameters.
        Returns a dictionary mapping enums to error msgs.
        """
        dictReturn = {}
        logging.debug(f"validateProfArgs({dictProfTgt}")

        exec_path = dictProfTgt["executeText"]
        exec_user = dictProfTgt["userText"]
        exec_pwd = dictProfTgt["dirText"]

        # Convert comma delimited string of "EnvVar=Value" substrings to dict
        exec_env = FaProfSession._comma_delimited_kv_string_to_dict(
            dictProfTgt["envText"]
        )

        # exec empty?
        if not exec_path:
            dictReturn[ProfSessionArgsStatus.EXEC_EMPTY] = s.PROF_ARG_EXEC_EMPTY

        else:
            # If absolute path
            if os.path.isabs(exec_path):
                # absolute and exists?
                if not os.path.exists(exec_path):
                    dictReturn[ProfSessionArgsStatus.EXEC_DOESNT_EXIST] = (
                        exec_path + s.PROF_ARG_EXEC_DOESNT_EXIST
                    )

                else:
                    # absolute and executable?
                    if not os.access(exec_path, os.X_OK):
                        dictReturn[ProfSessionArgsStatus.EXEC_NOT_EXEC] = (
                            exec_path + s.PROF_ARG_EXEC_NOT_EXEC
                        )
            else:
                # relative exec path
                # This creates an error on Rhel8.6: exec_env.get("PATH",""))
                # AttributeError: 'NoneType' object has no attribute 'get'
                exec_path = FaProfSession._rel_tgt_which(exec_path, exec_env)
                if not exec_path:
                    dictReturn[ProfSessionArgsStatus.EXEC_NOT_EXEC] = (
                        exec_path + s.PROF_ARG_EXEC_NOT_EXEC
                    )
        # user?
        try:
            if exec_user:
                pwd.getpwnam(exec_user)
        except KeyError as e:
            logging.debug(f"User {exec_user} does not exist: {e}")
            dictReturn[ProfSessionArgsStatus.USER_DOESNT_EXIST] = (
                exec_user + s.PROF_ARG_USER_DOESNT_EXIST
            )

        # working dir?
        # pwd empty?
        if exec_pwd:
            if not os.path.exists(exec_pwd):
                dictReturn[ProfSessionArgsStatus.PWD_DOESNT_EXIST] = (
                    exec_pwd + s.PROF_ARG_PWD_DOESNT_EXIST
                )

            elif not os.path.isdir(exec_pwd):
                dictReturn[ProfSessionArgsStatus.PWD_ISNT_DIR] = (
                    exec_pwd + s.PROF_ARG_PWD_ISNT_DIR
                )

        if not dictReturn:
            logging.debug("FaProfSession::validateArgs() --> pwd verified")

        return dictReturn or {ProfSessionArgsStatus.OK: s.PROF_ARG_OK}

    def _demote(enable, user_uid, user_gid):
        def result():
            os.setgid(user_gid)
            os.setuid(user_uid)

        return result if enable else None

    def _comma_delimited_kv_string_to_dict(string_in):
        """Generates dictionary from comma separated string of k=v pairs"""
        if not string_in:
            return None
        return {
            k: v.strip('"')
            for k, v in dict(x.strip().split("=") for x in string_in.split(",")).items()
        }


class FaProfiler:
    def __init__(self, fapd_mgr=None, fapd_persistance=True):
        logging.debug("FaProfiler::__init__()")
        self.fapd_mgr = fapd_mgr
        self.fapd_persistance = fapd_persistance
        self.fapd_pid = None
        self.fapd_prof_stdout = None
        self.fapd_prof_stderr = None
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
            self.fapd_prof_stdout = self.fapd_mgr.fapd_profiling_stdout
            self.fapd_prof_stderr = self.fapd_mgr.fapd_profiling_stderr

        try:
            self.faprofSession = FaProfSession(dictArgs, self)
        except ProfSessionException as e:
            logging.error(e)
            raise e

        key = dictArgs["executeText"] + "-" + str(self.instance)
        self.dictFaProfSession[key] = self.faprofSession
        try:
            self.faprofSession.startTarget(self.instance, block_until_term)
        except Exception as e:
            logging.error(e)
            raise e

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

        # Stop profiling targets first then stop fapd profiling instance
        if sessionName:
            self.dictFaProfSession[sessionName].stopTarget()
            del self.dictFaProfSession[sessionName]
        else:
            for k in list(self.dictFaProfSession):
                logging.debug(f"Stopping profiling session: {k}")
                self.dictFaProfSession[k].stopTarget()
                del self.dictFaProfSession[k]
        self.instance = 0
        self.fapd_mgr.stop(FapdMode.PROFILING)

    def get_profiling_timestamp(self):
        # Use FapdManager's start timestamp if available
        if self.fapd_mgr:
            self.strTimestamp = self.fapd_mgr._fapd_profiling_timestamp
        return self.strTimestamp
