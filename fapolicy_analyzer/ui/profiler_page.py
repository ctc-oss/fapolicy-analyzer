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
import glob
import logging
from events import Events
from time import sleep

import gi
from fapolicy_analyzer.ui.faprofiler import FaProfiler
from fapolicy_analyzer.ui.store import get_system_feature
from fapolicy_analyzer.ui.ui_page import UIAction, UIPage
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


class ProfilerPage(UIConnectedWidget, UIPage, Events):
    def __init__(self, fapd_manager):
        UIConnectedWidget.__init__(self, get_system_feature())
        self.__events__ = [
            "analyze_button_pushed",
            "reload_profiler",
            "store_profiler_entry",
        ]
        Events.__init__(self)
        actions = {
            "start": [
                UIAction(
                    "Start",
                    "Start Test",
                    "media-playback-start",
                    {"clicked": self.on_test_activate},
                    sensitivity_func=self.start_button_sensitivity,
                )
            ],
            "stop": [
                UIAction(
                    "Stop",
                    "Stop Test",
                    "media-playback-stop",
                    {},
                    sensitivity_func=self.stop_button_sensitivity,
                )
            ],
            "analyze": [
                UIAction(
                    "Analyze",
                    "Analyze Target",
                    "applications-science",
                    {"clicked": self.on_analyzerButton_clicked},
                )
            ],
            "reload": [
                UIAction(
                    "Reload",
                    "Reload Arguments",
                    "view-refresh",
                    {"clicked": self.on_reloadProfiler_clicked},
                )
            ],
        }

        UIPage.__init__(self, actions)
        self._fapd_profiler = FaProfiler(fapd_manager)
        self.running = False
        self.restore_args = None

    def on_analyzerButton_clicked(self, *args):
        self.analyze_button_pushed(self._fapd_profiler.fapd_prof_stderr)

    def on_reloadProfiler_clicked(self, *args):
        self.reload_profiler(True)
        prefixes = ["execute", "arg", "user", "dir", "env"]
        for prefix in prefixes:
            buff = self.get_object(prefix + "Entry").get_buffer()
            buff.set_text(self.restore_args[prefix + "Text"],
                          len(self.restore_args[prefix + "Text"])
                          )

    def stop_button_sensitivity(self):
        return self.running

    def start_button_sensitivity(self):
        return not self.running

    def get_entry_dict(self):
        entryDict = {
            "executeText": self.get_object("executeEntry").get_text(),
            "argText": self.get_object("argEntry").get_text(),
            "userText": self.get_object("userEntry").get_text(),
            "dirText": self.get_object("dirEntry").get_text(),
            "envText": self.get_object("envEntry").get_text(),
        }

        self.store_profiler_entry(entryDict)

        return entryDict

    def display_log_output(self):
        text_display = self.get_object("profilerOutput")
        buff = Gtk.TextBuffer()
        files = glob.glob("/tmp/*")
        time = self._fapd_profiler.get_profiling_timestamp()
        run_files = [f for f in files if time in f]
        if len(run_files) > 0:
            for run_file in run_files:
                buff.insert_markup(buff.get_end_iter(), f"<b>{run_file}</b>\n", -1)
                try:
                    with open(run_file, "r") as f:
                        lines = f.readlines()
                    buff.insert(buff.get_end_iter(), "".join(lines + ["\n"]))
                    buff.insert_markup(buff.get_end_iter(), "<b>" + "=" * len(run_file) + "</b>\n", -1)
                except OSError as ex:
                    logging.error(f"There was an issue reading from {run_file}.", ex)
        else:
            buff.insert(buff.get_start_iter(), "No files found.")
        text_display.set_buffer(buff)

    def on_test_activate(self, *args):
        profiling_args = self.get_entry_dict()
        self.restore_args = profiling_args
        logging.debug(f"Entry text = {profiling_args}")
        self.running = True
        self._fapd_profiler.fapd_persistance = self.get_object(
            "persistentCheckbox"
        ).get_active()
        self._fapd_profiler.start_prof_session(profiling_args)
        fapd_prof_stderr = self._fapd_profiler.fapd_prof_stderr
        logging.debug(f"Started prof session, stderr={fapd_prof_stderr}")

        sleep(4)
        self._fapd_profiler.stop_prof_session()
        self.display_log_output()
        self.running = False
