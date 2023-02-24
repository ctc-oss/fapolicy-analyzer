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
from fapolicy_analyzer.ui.reducers.profiler_reducer import ProfilerState
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
                )
            ],
        }

        UIPage.__init__(self, actions)
        self.can_start = True
        self.can_stop = False
        self.inputDict = {}
        self.markup = ""
        self.analysis_available = False
        self.analysis_file = ""

    def on_event(self, state: ProfilerState):
        self.can_start = not state.running
        self.can_stop = state.running
        self.analysis_available = bool(self.markup)
        self.refresh_toolbar()

        self.update_input_text(state.cmd, state.uid, state.pwd, state.env)

        if state.running:
            t = datetime.timedelta(seconds=state.duration) if state.duration else ""
            self.markup = f"<b>{state.pid}: Executing {state.cmd} {t}</b>"
            self.update_output_text(self.markup)
        else:
            self.display_log_output([state.events_log, state.stdout_log, state.stderr_log])

        self.analysis_file = state.events_log

    def update_input_text(self, cmd_string: Optional[str], uid: Optional[str], pwd: Optional[str], env: Optional[str]):
        (cmd, args) = cmd_string.split(" ", 1) if cmd_string and " " in cmd_string else [cmd_string, None]
        self.get_object("argText").set_text(args if args else "")
        self.get_object("executeText").set_text(cmd if cmd else "")
        self.get_object("userText").set_text(uid if uid else "")
        self.get_object("dirText").set_text(pwd if pwd else "")
        self.get_object("envText").set_text(env if env else "")

    def update_output_text(self, markup):
        self.markup = markup
        buff = Gtk.TextBuffer()
        buff.insert_markup(buff.get_end_iter(), markup, len(markup))
        self.get_object("profilerOutput").set_buffer(buff)

    def on_analyzer_button_clicked(self, *args):
        self.analyze_button_pushed(self.analysis_file)

    def on_clear_button_clicked(self, *args):
        dispatch(clear_profiler_state())

    def analyze_button_sensitivity(self):
        return self.analysis_available and self.can_start

    def stop_button_sensitivity(self):
        return self.can_stop

    def start_button_sensitivity(self):
        return self.can_start

    def _get_opt_text(self, named) -> Optional[str]:
        txt = self.get_object(named).get_text()
        return txt if txt else None

    def get_target_text(self) -> Optional[str]:
        return self._get_opt_text("executeText")

    def get_arg_text(self) -> Optional[str]:
        return self._get_opt_text("argText")

    def get_user_text(self) -> Optional[str]:
        return self._get_opt_text("userText")

    def get_pwd_text(self) -> Optional[str]:
        return self._get_opt_text("dirText")

    def get_env_text(self) -> Optional[str]:
        return self._get_opt_text("envText")

    def get_entry_dict(self):
        self.inputDict = {
            "executeText": self.get_target_text(),
            "argText": self.get_arg_text(),
            "userText": self.get_user_text(),
            "dirText": self.get_pwd_text(),
            "envText": self.get_env_text(),
        }
        return self.inputDict

    def display_log_output(self, logs):
        markup = ""
        for log in logs:
            if log:
                markup += f"<b>{log}</b>\n"
                try:
                    with open(log, "r") as f:
                        lines = f.readlines()
                    markup += html.escape("".join(lines + ["\n"]))
                    spacers = len(log)
                    markup += f"<b>{'=' * spacers}</b>\n"
                except OSError as ex:
                    logging.error(f"There was an issue reading from {log}", ex)
        self.update_output_text(markup)

    def on_stop_clicked(self, *args):
        self.can_stop = False
        self.refresh_toolbar()
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
            self.can_start = True
            self.refresh_toolbar()
        else:
            self.can_start = False
            self.refresh_toolbar()

            profiling_args["envDict"] = FaProfSession.comma_delimited_kv_string_to_dict(
                profiling_args.get("envText", "")
            )

            logging.debug(f"Entry text = {profiling_args}")
            dispatch(start_profiling(profiling_args))
