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

from typing import Callable

import gi
from rx import of
from rx.core.pipe import pipe
from rx.operators import catch, map

from fapolicy_analyzer import (start_stat_stream, StatStream)
from fapolicy_analyzer.redux import (
    Action,
    ReduxFeatureModule,
        combine_epics,
        of_type, create_feature_module,
)
from fapolicy_analyzer.ui.actions import  stats_started, terminating_stats, START_STATS_REQUEST, stats_initialization_error, STATS_KILL_REQUEST, stats_termination_error, stats_update
from fapolicy_analyzer.ui.reducers import stats_reducer


gi.require_version("Gtk", "3.0")
from gi.repository import GLib  # isort: skip

STATS_FEATURE = "stats"
_handle: StatStream # this needs to become stats handle

def create_stats_feature(dispatch: Callable) -> ReduxFeatureModule:
    stream_active: bool = False

    def _idle_dispatch(action: Action):
        GLib.idle_add(dispatch, action)

    def _on_recv(payload):
        (rec, ts) = payload
        _idle_dispatch(stats_update(rec.summary(), rec, ts))

    def _start_stat_stream(action: Action) -> Action:
        nonlocal stream_active
        global _handle

        f = "/var/run/fapolicyd/fapolicyd.state"

        if stream_active:
            return stats_started(f)

        stream_active = True

        _handle = start_stat_stream(f, _on_recv)

        return stats_started(f)

    def _kill_stat_stream(action: Action) -> Action:
        nonlocal stream_active
        global _handle

        if not stream_active:
            return action

        _handle.kill()
        stream_active = False

        return terminating_stats()

    start_stats_epic = pipe(
        of_type(START_STATS_REQUEST),
        map(_start_stat_stream),
        catch(lambda e, source: of(stats_initialization_error(str(e)))),
    )

    kill_stats_epic = pipe(
        of_type(STATS_KILL_REQUEST),
        map(_kill_stat_stream),
        catch(lambda e, source: of(stats_termination_error(str(e)))),
    )

    stats_epic = combine_epics(
        start_stats_epic,
        kill_stats_epic,
    )

    return create_feature_module(
        STATS_FEATURE, stats_reducer, epic=stats_epic
    )
