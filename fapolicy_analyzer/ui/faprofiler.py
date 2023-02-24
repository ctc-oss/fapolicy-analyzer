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
import shutil
from enum import Enum

import fapolicy_analyzer.ui.strings as s


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
    logging.debug(f"expand_path({colon_separated_str}, {cwd})")

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
        logging.info("validateArgs()")
        # Verify all keys are in dictProfTgt; delta_keys should be empty.
        expected_keys = {"executeText", "argText", "userText", "dirText", "envText"}
        delta_keys = expected_keys.difference(dictProfTgt.keys())
        if delta_keys:
            raise KeyError(f"Missing {delta_keys} key(s) from Profiler Page")

        dictReturn = {}
        logging.debug(f"validateArgs({dictProfTgt}")
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
