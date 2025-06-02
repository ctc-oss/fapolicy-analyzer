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
from fapolicy_analyzer.events import Events
from fapolicy_analyzer.ui.reducers.stats_reducer import StatsStreamState

from fapolicy_analyzer.ui.actions import (
    start_stats,
)
from fapolicy_analyzer.ui.stats.views import ObjCacheView, SubjCacheView, SlotsCacheView, EvictionCacheView

from fapolicy_analyzer.ui.ui_page import UIPage, UIAction
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget

from fapolicy_analyzer.ui.store import (
    dispatch,
    get_stats_feature,
)

from fapolicy_analyzer import signal_flush_cache


gi.require_version("Gtk", "3.0")

class StatsViewPage(UIConnectedWidget, UIPage, Events):
    def __init__(self):
        features = [
            {get_stats_feature(): {"on_next": self.on_event}},
        ]
        UIConnectedWidget.__init__(self, features=features)
        self.__events__ = []
        self._unsaved_changes = False
        Events.__init__(self)
        actions = {
            "stats": [
                UIAction(
                    "Flush",
                    "Flush Cache",
                    "edit-clear-symbolic",
                    {"clicked": self.on_flush_cache_clicked},
                )
            ],
        }
        UIPage.__init__(self, actions)
        self.__init_child_widgets()
        dispatch(start_stats())

    def __init_child_widgets(self):
        self.__text_view = self.get_object("profilerOutput")

        self.__lbox = self.get_object("lbox")
        self.__rbox = self.get_object("rbox")

        self.__obj_cache_view = ObjCacheView()
        self.__rbox.pack_start(self.__obj_cache_view.canvas, False, False, 10)

        self.__subj_cache_view = SubjCacheView()
        self.__rbox.pack_start(self.__subj_cache_view.canvas, False, False, 10)

        self.__slots_view = SlotsCacheView()
        self.__rbox.pack_start(self.__slots_view.canvas, False, False, 10)

        self.__eviction_view = EvictionCacheView()
        self.__lbox.pack_start(self.__eviction_view.canvas, False, False, 10)

        self.__obj_cache_view.canvas.show()
        self.__subj_cache_view.canvas.show()
        self.__slots_view.canvas.show()
        self.__eviction_view.canvas.show()

    def on_event(self, stats: StatsStreamState):
        if stats.summary is not None:
            self.__text_view.get_buffer().set_text(stats.summary)
            self.__obj_cache_view.on_event(stats)
            self.__subj_cache_view.on_event(stats)
            self.__slots_view.on_event(stats)
            self.__eviction_view.on_event(stats)

    def on_flush_cache_clicked(self, _):
        signal_flush_cache()
