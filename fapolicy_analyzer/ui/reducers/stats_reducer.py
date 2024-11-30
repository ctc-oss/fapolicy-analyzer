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

from typing import Any, NamedTuple, Optional
from fapolicy_analyzer.redux import Action, Reducer, handle_actions
from fapolicy_analyzer.ui.actions import START_STATS_REQUEST, START_STATS_RESPONSE, STATS_UPDATE
from fapolicy_analyzer import Rec, RecTs

class StatsStreamState(NamedTuple):
    summary: Optional[str]
    running: Optional[bool]
    rec: Optional[Rec]
    ts: Optional[RecTs]

class Started(StatsStreamState):
    pass


def empty_stats_state():
    return StatsStreamState(summary=None, rec=None, ts=None, running=None)

def derive_stats_state(
    target, source: StatsStreamState, **kwargs: Optional[Any]
) -> StatsStreamState:
    return target(**{**source._asdict(), **kwargs})


def handle_start_stats_request(
    state: StatsStreamState, action: Action
) -> StatsStreamState:
    return StatsStreamState(summary=state.summary, rec=state.rec, ts=state.ts, running=state.running)

def handle_start_stats_response(
    state: StatsStreamState, action: Action
) -> StatsStreamState:
    return StatsStreamState(summary=state.summary, rec=state.rec, ts=state.ts, running=True)

def handle_update_stats(
    state: StatsStreamState, action: Action
) -> StatsStreamState:
    (summary, rec, ts) = action.payload
    return StatsStreamState(summary=summary, rec=rec, ts=ts, running=True)


stats_reducer: Reducer = handle_actions(
    {
        START_STATS_REQUEST: handle_start_stats_request,
        START_STATS_RESPONSE: handle_start_stats_response,
        STATS_UPDATE: handle_update_stats,
    },
    empty_stats_state(),
)
