# Copyright Concurrent Technologies Corporation 2024
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


import gi
from events import Events
from fapolicy_analyzer.ui.reducers.stats_reducer import StatsStreamState

from fapolicy_analyzer.ui.actions import (
    request_config_text, start_stats,
)

from fapolicy_analyzer.ui.ui_page import UIPage, UIAction
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget

# from fapolicy_analyzer.ui.actions import ()
from fapolicy_analyzer.ui.store import (
    dispatch,
    get_system_feature, get_stats_feature,
)


import numpy as np

from matplotlib.backends.backend_gtk3agg import \
    FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.figure import Figure

from fapolicy_analyzer import signal_flush_cache


gi.require_version("Gtk", "3.0")


class StatsViewPage(UIConnectedWidget, UIPage, Events):
    def __init__(self):
        features = [
            {get_stats_feature(): {"on_next": self.on_event}},
        ]
        UIConnectedWidget.__init__(self, features=features)
        self.__events__ = [ "foo" ]
        self._unsaved_changes = False
        Events.__init__(self)
        actions = {
            "stats": [
                UIAction(
                    "Flush",
                    "Flush Cache",
                    "edit-clear",
                    {"clicked": self.on_clear_clicked},
                )
            ],
        }
        UIPage.__init__(self, actions)
        self.__init_child_widgets()

        dispatch(start_stats())

    def __init_child_widgets(self):
        self.__text_view: GtkTextView = self.get_object("profilerOutput")
        self.__vbox: GtkBox = self.get_object("vbox")

    def on_event(self, stats: StatsStreamState):
        if stats.summary is not None:
            self.__text_view.get_buffer().set_text(stats.summary)
        else:
            self.__text_view.get_buffer().set_text("")

    def on_clear_clicked(self, x):
        signal_flush_cache()

        figure = Figure(figsize=(5, 4), dpi=100)
        ax = figure.add_subplot(1, 1, 1)
        ax.plot([0, 1, 2, 3, 4], [0, 1, 4, 9, 16], label="y = x^2")  # Simple y = x^2 plot
        ax.set_title("Line Plot")
        ax.set_xlabel("X-axis")
        ax.set_ylabel("Y-axis")
        ax.legend()

        canvas = FigureCanvas(figure)
        canvas.set_size_request(300, 300)
        self.__vbox.pack_start(canvas, True, True, 0)
        canvas.show()
