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

import html
import logging
import datetime
import pwd
import os
import re

import pathlib
import shutil
from enum import Enum
from typing import Optional
import fapolicy_analyzer.ui.strings as s

import gi
from events import Events
from fapolicy_analyzer.ui.actions import (
    clear_profiler_state,
    start_profiling,
    stop_profiling,
)
from fapolicy_analyzer.ui.actions import NotificationType, add_notification
from fapolicy_analyzer.ui.reducers.profiler_reducer import (
    ProfilerState,
    ProfilerTick,
    ProfilerDone,
)
from fapolicy_analyzer.ui.store import dispatch, get_profiling_feature
from fapolicy_analyzer.ui.ui_page import UIAction, UIPage
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


class ProfArgsStatus(Enum):
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


class ProfArgsException(RuntimeError):
    def __init__(self, msg="Unknown error",
                 enumError=ProfArgsStatus.UNKNOWN):
        self.error_msg = f"Profiler Args: {msg}"
        self.error_enum = enumError


def EnumErrorPairs2Str(dictStatusEnums):
    """Converts the dict collection of profiler argument error to a string for
    displaying in the pop-up notification.
    """
    return "\n  ".join([f"Error: {r}" for r in (dictStatusEnums or {}).values()])


###########################################################################
# ProfilerPage methods
class ProfilerPage(UIConnectedWidget, UIPage, Events):
    def __init__(self, fapd_manager):
        # Profiler Page expanded atributes
        self._cmd = None
        self._arg = None
        self._uid = None
        self._pwd = None
        self._env = None

        UIConnectedWidget.__init__(
            self, get_profiling_feature(), on_next=self.on_event
        )
        self.__events__ = [
            "analyze_button_pushed",
            "refresh_toolbar",
        ]
        Events.__init__(self)
        actions = {
            "profiler": [
                UIAction(
                    "Start",
                    "Start Profiling",
                    "media-playback-start",
                    {"clicked": self.on_start_clicked},
                    sensitivity_func=self.start_button_sensitivity,
                ),
                UIAction(
                    "Stop",
                    "Stop Profiling",
                    "media-playback-stop",
                    {"clicked": self.on_stop_clicked},
                    sensitivity_func=self.stop_button_sensitivity,
                ),
                UIAction(
                    "Analyze",
                    "Analyze Output",
                    "applications-science",
                    {"clicked": self.on_analyzer_button_clicked},
                    sensitivity_func=self.analyze_button_sensitivity,
                ),
                UIAction(
                    "Clear",
                    "Clear Fields",
                    "edit-clear",
                    {"clicked": self.on_clear_button_clicked},
                    sensitivity_func=self.clear_button_sensitivity,
                )
            ],
        }

        UIPage.__init__(self, actions)
        self.needs_state = True
        self.can_start = True
        self.can_stop = False
        self.terminating = False
        self.input_error = False
        self.analysis_file = None
        self.markup = ""

        self.profiling_handlers = {
            ProfilerTick: self.handle_tick,
            ProfilerDone: self.handle_done,
        }

    def on_event(self, state: ProfilerState):
        self.refresh_view(state)
        if state.__class__ in self.profiling_handlers:
            self.profiling_handlers.get(state.__class__)(state)
        self.refresh_toolbar()

    def handle_tick(self, state: ProfilerTick):
        t = datetime.timedelta(seconds=state.duration) if state.duration else ""
        if self.terminating:
            self.update_output_text(".")
        else:
            self.markup = f"<span size='large'><b>{state.pid}: Executing {state.cmd} {t}</b></span>"
            self.set_output_text(self.markup)

    def handle_done(self, state: ProfilerState):
        self.display_log_output([
            (f"`{state.cmd}` stdout", state.stdout_log),
            (f"`{state.cmd}` stderr", state.stderr_log),
            ("fapolicyd", state.events_log),
        ])
        self.analysis_file = state.events_log
        self.terminating = False

    def update_input_fields(self, cmd_args: Optional[str], uid: Optional[str], pwd: Optional[str], env: Optional[str]):
        (cmd, args) = cmd_args.split(" ", 1) if cmd_args and " " in cmd_args else [cmd_args, None]
        self.get_object("argText").set_text(args if args else "")
        self.get_object("executeText").set_text(cmd if cmd else "")
        self.get_object("userText").set_text(uid if uid else "")
        self.get_object("dirText").set_text(pwd if pwd else "")
        self.get_object("envText").set_text(env if env else "")

    def clear_input_fields(self):
        self.update_input_fields(None, None, None, None)

    def clear_output_test(self):
        self.set_output_text(None)

    def set_output_text(self, markup):
        buff = Gtk.TextBuffer()
        if markup:
            self.markup = f"{markup}"
            buff.insert_markup(buff.get_end_iter(), markup, len(markup))
        self.get_object("profilerOutput").set_buffer(buff)

    def update_output_text(self, append):
        self.set_output_text(f"{self.markup}{append}")

    def refresh_view(self, state: ProfilerState):
        self.can_start = not state.running
        self.can_stop = state.running
        if self.needs_state:
            self.needs_state = False
            self.update_input_fields(state.cmd, state.uid, state.pwd, state.env)

    def on_analyzer_button_clicked(self, *args):
        self.analyze_button_pushed(self.analysis_file)

    def on_clear_button_clicked(self, *args):
        self.clear_output_test()
        self.clear_input_fields()
        self.analysis_file = None
        dispatch(clear_profiler_state())

    def analyze_button_sensitivity(self):
        return self.start_button_sensitivity() and self.analysis_file is not None

    def clear_button_sensitivity(self):
        return self.start_button_sensitivity()

    def stop_button_sensitivity(self):
        return self.can_stop

    def start_button_sensitivity(self):
        return self.can_start

    def _get_opt_text(self, named) -> Optional[str]:
        txt = self.get_object(named).get_text()
        return txt if txt else None

    def get_cmd_text(self) -> Optional[str]:
        return self._get_opt_text("executeText")

    def get_arg_text(self) -> Optional[str]:
        return self._get_opt_text("argText")

    def get_uid_text(self) -> Optional[str]:
        return self._get_opt_text("userText")

    def get_pwd_text(self) -> Optional[str]:
        return self._get_opt_text("dirText")

    def get_env_text(self) -> Optional[str]:
        return self._get_opt_text("envText")

    def get_entry_dict(self):
        """ Get Profiler UI field contents and set object attributes
        """
        self._cmd = self.get_cmd_text()
        self._arg = self.get_arg_text()
        self._uid = self.get_uid_text()
        self._pwd = self.get_pwd_text()
        self._env = self.get_env_text()
        return {
            "cmd": self._cmd if self._cmd else None,
            "arg": self._arg if self._arg else None,
            "uid": self._uid if self._uid else None,
            "pwd": self._pwd if self._pwd else None,
            "env": self._env if self._env else None,
        }

    def get_entry_dict_markup(self):
        return "<span size='x-large' underline='single'><b>Target</b></span>\n" + \
            "\n".join([f"{key}: {value}" for key, value in self.get_entry_dict().items()])

    def display_log_output(self, logs):
        markup = self.get_entry_dict_markup() + "\n\n"
        for (description, log) in logs:
            if log:
                markup += f"<span size='x-large' underline='single'><b>{description}</b></span> (<b>{log}</b>)\n"
                try:
                    with open(log, "r") as f:
                        lines = f.readlines()
                    markup += html.escape("".join(lines + ["\n"]))
                except OSError as ex:
                    logging.error(f"There was an issue reading from {log}", ex)
                    markup += f"<span size='large'>Failed to open log: <span underline='error'>{ex}</span></span>\n"
                markup += "\n\n"
        self.set_output_text(markup.rstrip())

    def on_stop_clicked(self, *args):
        self.can_stop = False
        self.terminating = True
        self.refresh_toolbar()
        self.update_output_text("\n<span size='large'><b>Profiler terminating...</b></span>")
        dispatch(stop_profiling())

    def on_start_clicked(self, *args):
        profiling_args = self.get_entry_dict()
        if not FaProfArgs.validSessionArgs(profiling_args):
            logging.info("Invalid Profiler arguments")
            dictInvalidEnums = FaProfArgs.validateArgs(profiling_args)
            strStatusEnums = "\n  " + EnumErrorPairs2Str(dictInvalidEnums)
            dispatch(
                add_notification(
                    f"Invalid Profiler Session argument(s): {strStatusEnums}",
                    NotificationType.ERROR,
                )
            )
            self.input_error = True
            self.can_start = True
            self.terminating = False
            self.refresh_toolbar()
        else:
            self.input_error = False
            self.can_start = False
            self.terminating = False
            self.refresh_toolbar()

            self.set_output_text("<span size='large'><b>Profiler starting...</b></span>")

            profiling_args = self._make_profiling_args()

            logging.debug(f"Entry text = {profiling_args}")
            dispatch(start_profiling(profiling_args))

    def _make_profiling_args(self):
        res = dict(self.get_entry_dict())
        logging.debug(f"make_profiling_args(): form args = {res}")
        res = _args_user_home_expansion(res)
        logging.debug(f"make_profiling_args(): expanded form args = {res}")
        d = FaProfArgs.comma_delimited_kv_string_to_dict(res.get("env", ""))
        if d and "PATH" in d:
            d["PATH"] = expand_path(d.get("PATH"), res.get("pwd", ".") or ".")
        res["env_dict"] = d
        logging.debug(f"_make_profiling_args(): args w/env dict = {res}")
        return res


class FaProfArgs:
    @staticmethod
    def which(dictProfTgt):
        FaProfArgs.throwOnInvalidSessionArgs(dictProfTgt)
        return FaProfArgs._rel_tgt_which(
            dictProfTgt.get("cmd", ""),
            FaProfArgs.comma_delimited_kv_string_to_dict(dictProfTgt.get("env", "")),
            dictProfTgt.get("pwd", "")
        )

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
        return ProfArgsStatus.OK in FaProfArgs.validateArgs(dictProfTgt)

    @staticmethod
    def throwOnInvalidSessionArgs(dictProfTgt):
        """Throw exception on first invalid Profiler session argument."""
        dictInvalidEnums = FaProfArgs.validateArgs(dictProfTgt)
        if ProfArgsStatus.OK not in dictInvalidEnums:
            error_enum = next(iter(dictInvalidEnums))
            error_msg = dictInvalidEnums.get(error_enum)
            raise ProfArgsException(error_msg, error_enum)

    @staticmethod
    def validateArgs(dictProfTgt):
        """
        Validates the Profiler Args object's user, target, pwd parameters.
        Returns a dictionary mapping enums to error msgs w/original entry text
        """
        logging.info("validateArgs()")
        # Verify all keys are in dictProfTgt; delta_keys should be empty.
        expected_keys = {"cmd", "arg", "uid", "pwd", "env"}
        delta_keys = expected_keys.difference(dictProfTgt.keys())
        if delta_keys:
            raise KeyError(f"Missing {delta_keys} key(s) from Profiler Page")

        dictReturn = {}
        logging.debug(f"validateArgs({dictProfTgt}")
        dict_expanded_args = _args_user_home_expansion(dictProfTgt)
        exec_path = dictProfTgt.get("cmd", "")
        exec_user = dictProfTgt.get("uid", "")
        orig_pwd = dictProfTgt.get("pwd", "")
        exec_pwd = dict_expanded_args.get("pwd", "")

        # user?
        user_pw_record = None  # passwd file record associated with a user
        try:
            if exec_user:
                user_pw_record = pwd.getpwnam(exec_user)
        except KeyError as e:
            logging.debug(f"User {exec_user} does not exist: {e}")
            dictReturn[ProfArgsStatus.USER_DOESNT_EXIST] = (
                exec_user + s.PROF_ARG_USER_DOESNT_EXIST
            )

        # working dir?
        # Verify expanded pwd up-front  because it is used with relative exec
        # paths as the current working dir
        if exec_pwd:
            logging.debug(f"Processing current working dir: {exec_pwd}")
            if not os.path.exists(exec_pwd):
                dictReturn[ProfArgsStatus.PWD_DOESNT_EXIST] = (
                    orig_pwd + s.PROF_ARG_PWD_DOESNT_EXIST
                )

            elif not os.path.isdir(exec_pwd):
                dictReturn[ProfArgsStatus.PWD_ISNT_DIR] = (
                    orig_pwd + s.PROF_ARG_PWD_ISNT_DIR
                )
        else:
            # If valid user is specified and working dir is not, use user's HOME
            if user_pw_record:
                exec_pwd = user_pw_record.pw_dir
            else:
                exec_pwd = os.getcwd()

        if not dictReturn:
            logging.debug("FaProfArgs::validateArgs() --> pwd verified")

        # Validate, convert CSV  env string of "K=V" substrings to dict
        try:
            exec_env = FaProfArgs.comma_delimited_kv_string_to_dict(
                dictProfTgt.get("env", "")
            )

        except RuntimeError as e:
            exec_env = None
            dictReturn[ProfArgsStatus.ENV_VARS_FORMATING] = e
        except Exception as e:
            exec_env = None
            dictReturn[ProfArgsStatus.ENV_VARS_FORMATING] = s.PROF_ARG_ENV_VARS_FORMATING + f", {e}"

        # exec empty?
        if not exec_path:
            dictReturn[ProfArgsStatus.EXEC_EMPTY] = s.PROF_ARG_EXEC_EMPTY

        else:
            # If absolute path
            if os.path.isabs(exec_path):
                # absolute and exists?
                if not os.path.exists(exec_path):
                    dictReturn[ProfArgsStatus.EXEC_DOESNT_EXIST] = (
                        exec_path + s.PROF_ARG_EXEC_DOESNT_EXIST
                    )

                else:
                    # absolute and executable?
                    if not os.access(exec_path, os.X_OK):
                        dictReturn[ProfArgsStatus.EXEC_NOT_EXEC] = (
                            exec_path + s.PROF_ARG_EXEC_NOT_EXEC
                        )
            else:
                # relative exec path
                new_path = FaProfArgs._rel_tgt_which(exec_path,
                                                     exec_env,
                                                     exec_pwd)
                if not new_path:
                    dictReturn[ProfArgsStatus.EXEC_NOT_FOUND] = (
                        exec_path + s.PROF_ARG_EXEC_NOT_FOUND
                    )
                else:
                    # Convert relative exec path to absolute exec path
                    exec_path = new_path

        return dictReturn or {ProfArgsStatus.OK: s.PROF_ARG_OK}

    @staticmethod
    def comma_delimited_kv_string_to_dict(string_in):
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


###########################################################################
#                            Utility Functions
def _expand_user_home(str_in, user, home):
    """Expand $HOME and $USER strings in the str_in string"""
    logging.debug(f"_expand_user_home({str_in}, {user}, {home})")
    if user:
        str_in = re.sub(r"\$USER", user, str_in)
    if home:
        str_in = re.sub(r"\$HOME", home, str_in)
    logging.debug(f"Return: {str_in}")
    return str_in


def _args_user_home_expansion(dict_args):
    """Expand $HOME and $USER strings in the pwd, env, and arg fields"""
    logging.debug(f"_args_user_home_expansion(in): {dict_args}")
    if dict_args["uid"]:
        # Use specified user and verify it is valid
        username = dict_args["uid"]
        try:
            user_pw_record = pwd.getpwnam(username)
        except Exception:
            user_id = os.getuid()
            user_pw_record = pwd.getpwuid(user_id)
    else:
        # Otherwise use effective user
        user_id = os.getuid()
        user_pw_record = pwd.getpwuid(user_id)
    username = user_pw_record.pw_name
    homedir = user_pw_record.pw_dir

    for k in dict_args:
        if (k == "pwd" or k == "env" or k == "arg") and dict_args[k]:
            dict_args[k] = _expand_user_home(dict_args[k], username, homedir)

    # Populate pwd field w/user home if uid specified and pwd empty
    if not dict_args["pwd"]:
        dict_args["pwd"] = homedir

    logging.debug(f"_args_user_home_expansion(out): {dict_args}")
    return dict_args


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
