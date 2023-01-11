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
import pathlib
import pwd
import re
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
    EXEC_NOT_FOUND = 4
    USER_DOESNT_EXIST = 5
    PWD_DOESNT_EXIST = 6
    PWD_ISNT_DIR = 7,
    ENV_VARS_FORMATING = 8,
    UNKNOWN = 9


# ########################## Utility Functions ###########################
def EnumErrorPairs2Str(dictStatusEnums):
    """Converts the dict collection of profiler argument error to a string for
    displaying in the pop-up notification.
    """
    return "\n  ".join([f"Error: {r}" for r in (dictStatusEnums or {}).values()])


def expand_path(colon_separated_str, cwd="."):
    """Expands user supplied PATH argument that contains embedded 'PATH'
    variable, leading colon, terminating colon, or an intermediate double colon.
    These final three colon notations map to the user supplied working dir.
    """
    logging.info(f"expand_path({colon_separated_str}, {cwd})")

    # Expand native PATH env var if in user provided PATH env var string
    expanded_path = re.sub(r"\$\{?PATH\}?",
                           os.environ.get("PATH"), colon_separated_str)

    # Expand implied and explicit '.' notation to supplied cwd argument
    expanded_path = re.sub(r":\.{0,1}$", f":{cwd}", expanded_path)
    expanded_path = re.sub(r"^\.{0,1}:", f"{cwd}:", expanded_path)
    expanded_path = re.sub(r":\.{0,1}:", "f:{cwd}:", expanded_path)
    expanded_path = re.sub(r"^\.$", f"{cwd}", expanded_path)

    # Similarly substitute parent of cwd for double periods when possible
    path_cwd = pathlib.Path(cwd)
    ppath_cwd = path_cwd.parent
    if ppath_cwd != path_cwd:
        expanded_path = re.sub(r"\.\.", f"{ppath_cwd}", expanded_path)

    logging.debug(f"expand_path::path = {expanded_path}")
    return expanded_path


class ProfSessionException(RuntimeError):
    def __init__(self, msg="Unknown error",
                 enumError=ProfSessionArgsStatus.UNKNOWN):
        self.error_msg = f"Profiler Session: {msg}"
        self.error_enum = enumError


# ########################## Profiler Session ###########################
class FaProfSession:
    def __init__(self, dictProfTgt, instance=0, faprofiler=None):
        logging.info(f"faProfSession::__init__({dictProfTgt}, {faprofiler})")
        self.throwOnInvalidSessionArgs(dictProfTgt)
        self.timeStamp = None

        # euid, working directory and environment variables
        self.user = dictProfTgt.get("userText", "")

        # Set pwd - Use current dir for pwd if not supplied by user
        self.pwd = dictProfTgt.get("dirText") or os.getcwd()

        # Convert comma delimited string of "EnvVar=Value" substrings to dict
        self.env = FaProfSession._comma_delimited_kv_string_to_dict(
            dictProfTgt.get("envText", "")
        )

        # expand and update path if user supplied
        # Use user provided PATH otherwise use env var PATH, also expand periods
        # with specified cwd arg value or the default current working dir.
        if self.env and "PATH" in self.env:
            search_path = self.env.get("PATH")

            # Substitute the cwd for any periods or bare colons in  path
            search_path = expand_path(search_path, self.pwd)

            # Update the PATH in self.env because it will be provided to Popen()
            self.env["PATH"] = search_path
        else:
            search_path = os.getenv("PATH")

        # Executable command and arguments
        user_provided_exec = dictProfTgt.get("executeText", "")
        if os.path.isabs(user_provided_exec):
            self.execPath = user_provided_exec
        else:
            self.execPath = FaProfSession._rel_tgt_which(user_provided_exec,
                                                         self.env,
                                                         self.pwd)
        logging.debug(f"exec={self.execPath}, Profiling PATH = {search_path}")

        self.execArgs = dictProfTgt.get("argText", "")
        self.listCmdLine = [self.execPath] + self.execArgs.split()

        self.faprofiler = faprofiler
        self.name = os.path.basename(self.execPath)
        self.timeStamp = self._get_profiling_timestamp()
        self.abs_baselogname = f"/tmp/tgt_profiling_{self.timeStamp}_{self.name}"

        self.status = ProfSessionStatus.QUEUED
        self.procTarget = None

        # Temp demo workaround for setting target log file paths
        log_dir = os.environ.get("FAPD_LOGPATH")
        if log_dir:
            self.tgtStdout = f"{log_dir}_{self.name}.stdout"
            self.tgtStderr = f"{log_dir}_{self.name}.stderr"
        else:
            self.tgtStdout = f"{self.abs_baselogname}_{instance}.stdout"
            self.tgtStderr = f"{self.abs_baselogname}_{instance}.stderr"

        # File descriptors are state variables; closed in stopTarget()
        self.fdTgtStdout = None
        self.fdTgtStderr = None

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

        # Convert username to uid/gid
        self.u_valid = False
        try:
            if self.user:
                # Get uid/gid of new user and the associated default group
                pw_record = pwd.getpwnam(self.user)
                self.uid = pw_record.pw_uid
                self.gid = pw_record.pw_gid
                logging.info(f"The uid/gid of the profiling tgt: {self.uid}/{self.gid}")

                # Change the ownership of profiling tgt's stdout and stderr
                logging.info(
                    f"Changing ownership of fds: {self.fdTgtStdout},{self.fdTgtStderr}"
                )
                os.fchown(self.fdTgtStdout.fileno(), self.uid, self.gid)
                os.fchown(self.fdTgtStderr.fileno(), self.uid, self.gid)
                logging.info(
                    f"Changed the profiling tgt stdout/err ownership {self.uid},{self.gid}"
                )
                self.u_valid = True
            else:
                # In production, the following will be the superuser defaults
                self.uid = os.getuid()
                self.gid = os.getgid()

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

            self.uid = os.getuid()  # Place holder args to _demote()
            self.gid = os.getgid()

    def startTarget(self, block_until_termination=True):
        logging.info("FaProfSession::startTarget()")

        # Capture process object
        try:
            logging.debug(f"Starting {self.listCmdLine} as {self.uid}/{self.gid}")
            logging.debug(f"in {self.pwd} with env: {self.env}")
            self.procTarget = subprocess.Popen(
                self.listCmdLine,
                stdout=self.fdTgtStdout,
                stderr=self.fdTgtStderr,
                cwd=self.pwd,
                env=self.env,
                preexec_fn=FaProfSession._demote(self.u_valid,
                                                 self.uid,
                                                 self.gid)
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

    def _get_profiling_timestamp(self):
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
        logging.info("FaProfSession::get_status()")

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
        logging.info("FaProfSession::clean_all()")
        # Delete all log file artifacts

    @staticmethod
    def _rel_tgt_which(relative_exec, user_provided_env, working_dir):
        """
        Given a specified relative executable and a colon separated PATH string
        or the environment PATH variable return the absolute path of executable
        """

        # Use user provided PATH otherwise use env var PATH, also expand periods
        # with specified cwd arg value or the default current working dir.
        if user_provided_env and "PATH" in user_provided_env:
            search_path = user_provided_env.get("PATH")
        else:
            search_path = os.getenv("PATH")

        # Substitute the current working dir for any periods or colons in  path
        search_path = expand_path(search_path, working_dir)
        logging.debug(f"exec={relative_exec}, Profiling PATH = {search_path}")

        # If exec path exist, convert to absolute path if needed
        discovered_exec_path = shutil.which(relative_exec, path=search_path)
        if discovered_exec_path and not os.path.isabs(discovered_exec_path):
            discovered_exec_path = os.path.abspath(discovered_exec_path)
        logging.info(f"_rel_tgt_which() - return value:{discovered_exec_path}")
        return discovered_exec_path

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
            error_msg = dictInvalidEnums.get(error_enum)
            raise ProfSessionException(error_msg, error_enum)

    @staticmethod
    def validateArgs(dictProfTgt):
        """
        Validates the Profiler Session object's user, target, pwd parameters.
        Returns a dictionary mapping enums to error msgs.
        """

        # Verify all keys are in dictProfTgt; delta_keys should be empty.
        expected_keys = set(["executeText",
                             "argText",
                             "userText",
                             "dirText",
                             "envText"])
        delta_keys = expected_keys.difference(dictProfTgt.keys())
        if delta_keys:
            raise KeyError(f"Missing {delta_keys} key(s) from Profiler Page")

        dictReturn = {}
        logging.info(f"validateArgs({dictProfTgt}")
        exec_path = dictProfTgt.get("executeText", "")
        exec_user = dictProfTgt.get("userText", "")
        exec_pwd = dictProfTgt.get("dirText", "")

        # working dir?
        # pwd empty? Check pwd first because it is used with relative exec paths
        # as the current working dir
        if exec_pwd:
            logging.debug(f"Processing current working dir: {exec_pwd}")
            if not os.path.exists(exec_pwd):
                dictReturn[ProfSessionArgsStatus.PWD_DOESNT_EXIST] = (
                    exec_pwd + s.PROF_ARG_PWD_DOESNT_EXIST
                )

            elif not os.path.isdir(exec_pwd):
                dictReturn[ProfSessionArgsStatus.PWD_ISNT_DIR] = (
                    exec_pwd + s.PROF_ARG_PWD_ISNT_DIR
                )
        else:
            # Set it if not set
            exec_pwd = os.getcwd()

        if not dictReturn:
            logging.debug("FaProfSession::validateArgs() --> pwd verified")

        # Validate, convert CSV  env string of "K=V" substrings to dict
        try:
            exec_env = FaProfSession._comma_delimited_kv_string_to_dict(
                dictProfTgt.get("envText", "")
            )

        except RuntimeError as e:
            exec_env = None
            dictReturn[ProfSessionArgsStatus.ENV_VARS_FORMATING] = e
        except Exception as e:
            exec_env = None
            dictReturn[ProfSessionArgsStatus.ENV_VARS_FORMATING] = s.PROF_ARG_ENV_VARS_FORMATING + f", {e}"

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
                new_path = FaProfSession._rel_tgt_which(exec_path,
                                                        exec_env,
                                                        exec_pwd)
                if not new_path:
                    dictReturn[ProfSessionArgsStatus.EXEC_NOT_FOUND] = (
                        exec_path + s.PROF_ARG_EXEC_NOT_FOUND
                    )
                else:
                    # Convert relative exec path to absolute exec path
                    exec_path = new_path
        # user?
        try:
            if exec_user:
                pwd.getpwnam(exec_user)
        except KeyError as e:
            logging.debug(f"User {exec_user} does not exist: {e}")
            dictReturn[ProfSessionArgsStatus.USER_DOESNT_EXIST] = (
                exec_user + s.PROF_ARG_USER_DOESNT_EXIST
            )

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

        dictReturn = {
            k: v.strip('"')
            for k, v in dict(x.strip().split("=") for x in string_in.split(",")).items()
        }
        # Verify keys are only letters and underscores
        for k in dictReturn.keys():
            if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", k):
                raise RuntimeError(s.PROF_ARG_ENV_VARS_NAME_BAD + f": ' {k} '")
        return dictReturn


# ############################## Profiler ###############################
class FaProfiler:
    def __init__(self, fapd_mgr=None, fapd_persistance=True):
        logging.info("FaProfiler::__init__()")
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
        logging.info(f"FaProfiler::start_prof_session('{dictArgs}')")
        self.fapd_mgr.start(FapdMode.PROFILING)
        if self.fapd_mgr.procProfile:
            self.fapd_pid = self.fapd_mgr.procProfile.pid
            self.fapd_prof_stdout = self.fapd_mgr.fapd_profiling_stdout
            self.fapd_prof_stderr = self.fapd_mgr.fapd_profiling_stderr

        try:
            self.faprofSession = FaProfSession(dictArgs, self.instance, self)
        except ProfSessionException as e:
            logging.error(e)
            raise e

        key = dictArgs.get("executeText", "") + "-" + str(self.instance)
        self.dictFaProfSession[key] = self.faprofSession
        try:
            self.faprofSession.startTarget(block_until_term)
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
        logging.info("FaProfiler::status_prof_session()")
        return self.dictFaProfSession.get(sessionName).get_status()

    def stop_prof_session(self, sessionName=None):
        logging.info("FaProfiler::stop_prof_session()")

        # Stop profiling targets first then stop fapd profiling instance
        if sessionName:
            self.dictFaProfSession.get(sessionName).stopTarget()
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
