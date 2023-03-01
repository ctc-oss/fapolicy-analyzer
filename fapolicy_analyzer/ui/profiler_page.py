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
from typing import Optional

import gi
from events import Events
from fapolicy_analyzer.ui.actions import (
    clear_profiler_state,
    start_profiling,
    stop_profiling,
)
from fapolicy_analyzer.ui.actions import NotificationType, add_notification
from fapolicy_analyzer.ui.faprofiler import (
    EnumErrorPairs2Str, FaProfSession,
)
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


class ProfilerPage(UIConnectedWidget, UIPage, Events):
    def __init__(self, fapd_manager):
        UIConnectedWidget.__init__(
            self, get_profiling_feature(), on_next=self.on_event
        )
        self.__events__ = [
            "analyze_button_pushed",
            "refresh_toolbar",
        ]
        Events.__init__(self)
        actions = {
            "start": [
                UIAction(
                    "Start",
                    "Start Profiling",
                    "media-playback-start",
                    {"clicked": self.on_start_clicked},
                    sensitivity_func=self.start_button_sensitivity,
                )
            ],
            "stop": [
                UIAction(
                    "Stop",
                    "Stop Profiling",
                    "media-playback-stop",
                    {"clicked": self.on_stop_clicked},
                    sensitivity_func=self.stop_button_sensitivity,
                )
            ],
            "analyze": [
                UIAction(
                    "Analyze",
                    "Analyze Output",
                    "applications-science",
                    {"clicked": self.on_analyzer_button_clicked},
                    sensitivity_func=self.analyze_button_sensitivity,
                )
            ],
            "clear": [
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
        if state.__class__ in self.profiling_handlers:
            self.profiling_handlers.get(state.__class__)(state)
        self.refresh_view(state)
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
            ("fapolicyd stdout", state.events_log),
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
        return {
            "cmd": self.get_cmd_text(),
            "arg": self.get_arg_text(),
            "uid": self.get_uid_text(),
            "pwd": self.get_pwd_text(),
            "env": self.get_env_text(),
        }

    def display_log_output(self, logs):
        markup = ""
        for (description, log) in logs:
            if log:
                markup += f"<span size='x-large' underline='single'><b>{description}</b></span> (log)\n"
                try:
                    with open(log, "r") as f:
                        lines = f.readlines()
                    markup += html.escape("".join(lines + ["\n"]))
                except OSError as ex:
                    logging.error(f"There was an issue reading from {log}", ex)
                    markup += f"<span size='large'>Failed to open log: <span underline='error'>{ex}</span></span>\n"
                markup += "\n\n"
        self.set_output_text(markup)

    def on_stop_clicked(self, *args):
        self.can_stop = False
        self.terminating = True
        self.refresh_toolbar()
        self.update_output_text("\n<span size='large'><b>Profiler terminating...</b></span>")
        dispatch(stop_profiling())

    def on_start_clicked(self, *args):
        profiling_args = self.get_entry_dict()
        if not FaProfSession.validSessionArgs(profiling_args):
            logging.info("Invalid Profiler arguments")
            dictInvalidEnums = FaProfSession.validateArgs(profiling_args)
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

            profiling_args = self.make_profiling_args()

            logging.debug(f"Entry text = {profiling_args}")
            dispatch(start_profiling(profiling_args))

    def make_profiling_args(self):
        res = dict(self.get_entry_dict())
        res["env_dict"] = FaProfSession.comma_delimited_kv_string_to_dict(
            res.get("env", "")
        )
        return res
