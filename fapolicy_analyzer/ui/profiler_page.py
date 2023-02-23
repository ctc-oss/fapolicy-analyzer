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
    set_profiler_output,
    start_profiling,
    stop_profiling,
)
from fapolicy_analyzer.ui.actions import NotificationType, add_notification
from fapolicy_analyzer.ui.faprofiler import (
    EnumErrorPairs2Str,
)
from fapolicy_analyzer.ui.reducers.profiler_reducer import ProfilerState
from fapolicy_analyzer.ui.store import dispatch, get_system_feature, get_profiling_feature
from fapolicy_analyzer.ui.ui_page import UIAction, UIPage
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip
from gi.repository import GLib  # isort: skip


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
                    {"clicked": self.on_analyzerButton_clicked},
                    sensitivity_func=self.analyze_button_sensitivity,
                )
            ],
            "clear": [
                UIAction(
                    "Clear",
                    "Clear Fields",
                    "edit-clear",
                    {"clicked": self.on_clearButton_clicked},
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

    def analyze_button_sensitivity(self):
        return self.analysis_available and self.can_start

    def on_event(self, state: ProfilerState):
        self.can_start = not state.running
        self.can_stop = state.running
        self.analysis_available = bool(self.markup)
        self.refresh_toolbar()

        self.update_field_text(state.cmd, state.user, state.pwd, state.env)

        if state.running:
            t = datetime.timedelta(seconds=state.duration) if state.duration else ""
            self.markup = f"<b>{state.pid}: Executing {state.cmd} {t}</b>"
            self.update_output_text(self.markup)
        else:
            print(f"displaying log output, {state.events_log}, {state.stdout_log}, {state.stderr_log}")
            self.display_log_output([state.events_log, state.stdout_log, state.stderr_log])

        self.analysis_file = state.events_log

    def update_field_text(self, cmd_string: Optional[str], user: Optional[str], pwd: Optional[str], env: Optional[str]):
        if cmd_string:
            (cmd, args) = cmd_string.split(" ", 1)
            self.get_object("executeText").set_text(cmd if cmd else "")
            self.get_object("argText").set_text(args if args else "")

    def update_output_text(self, markup):
        self.markup = markup
        buff = Gtk.TextBuffer()
        buff.insert_markup(buff.get_end_iter(), markup, len(markup))
        self.get_object("profilerOutput").set_buffer(buff)

    def on_analyzerButton_clicked(self, *args):
        self.analyze_button_pushed(self.analysis_file)

    def on_clearButton_clicked(self, *args):
        dispatch(clear_profiler_state())

    def stop_button_sensitivity(self):
        return self.can_stop

    def start_button_sensitivity(self):
        return self.can_start

    def get_entry_dict(self):
        self.inputDict = {
            "executeText": self.get_object("executeText").get_text(),
            "argText": self.get_object("argText").get_text(),
            "userText": self.get_object("userText").get_text(),
            "dirText": self.get_object("dirText").get_text(),
            "envText": self.get_object("envText").get_text(),
        }
        return self.inputDict

    def display_log_output(self, logs):
        markup = ""
        for log in logs:
            if log:
                print(f"displaying log: {log}")
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

    def on_execd(self, h):
        self.can_stop = True
        dispatch(set_profiler_output(f"<b>{h.pid}: Executing {h.cmd}</b>"))
        GLib.idle_add(self.refresh_toolbar)
        logging.debug(f"profiling started {h.pid}: {h.cmd}")

    def on_tick(self, h, d):
        t = datetime.timedelta(seconds=d)
        dispatch(set_profiler_output(f"<b>{h.pid}: Executing {h.cmd} {t}</b>"))

    def on_done(self):
        self.can_start = True
        self.display_log_output()
        GLib.idle_add(self.refresh_toolbar)

    def on_stop_clicked(self, *args):
        self.can_stop = False
        self.refresh_toolbar()
        dispatch(stop_profiling())

    def on_start_clicked(self, *args):
        self.can_start = False
        self.refresh_toolbar()

        profiling_args = self.get_entry_dict()
        # todo-redux;; validation
        # if not FaProfSession.validSessionArgs(profiling_args):
        #     logging.info("Invalid Profiler arguments")
        #     dictInvalidEnums = FaProfSession.validateArgs(profiling_args)
        #     strStatusEnums = "\n  " + EnumErrorPairs2Str(dictInvalidEnums)
        #     dispatch(
        #         add_notification(
        #             f"Invalid Profiler Session argument(s): {strStatusEnums}",
        #             NotificationType.ERROR,
        #         )
        #     )
        #     self.can_start = True
        #     self.refresh_toolbar()
        #     return

        logging.debug(f"Entry text = {profiling_args}")
        # todo;; revise the persistence stuff
        # self._fapd_profiler.fapd_persistance = self.get_object(
        #     "persistentCheckbox"
        # ).get_active()

        # todo-redux;; start profiling
        # self._fapd_profiler.start_prof_session(profiling_args, self.on_execd, self.on_tick, self.on_done)
        dispatch(start_profiling(profiling_args))

        # todo-redux;; handle arg errors
        # except ProfSessionException as e:
        #     # Profiler Session creation failed because of bad args
        #     logging.debug(f"{e.error_msg}, {e.error_enum}")
        #     dispatch(
        #         add_notification(
        #             e.error_msg,
        #             NotificationType.ERROR,
        #         )
        #     )

        # todo-redux;; handle profiling errors
        # except Exception as e:
        #     logging.debug(f"Unknown exception thrown by start_prof_session {e}")
        #     dispatch(
        #         add_notification(
        #             "Error: An unknown Profiler Session error has occured.",
        #             NotificationType.ERROR,
        #         )
        #     )
