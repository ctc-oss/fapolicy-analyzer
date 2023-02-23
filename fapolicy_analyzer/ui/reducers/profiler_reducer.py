# Copyright Concurrent Technologies Corporation 2022
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

from typing import Any, Dict, NamedTuple, Optional, cast

from fapolicy_analyzer.redux import Action, Reducer, handle_actions
from fapolicy_analyzer.ui.actions import (
    CLEAR_PROFILER_STATE,
    SET_PROFILER_OUTPUT,
    SET_PROFILER_ANALYSIS_FILE,
    SET_PROFILER_STATE,
    PROFILING_EXEC,
    PROFILING_DONE, PROFILING_INIT, PROFILING_STARTED,
)


class ProfilerState(NamedTuple):
    entry: Dict[str, str]
    output: str
    file: str
    running: bool


default_entry = {"executeText": "",
                 "argText": "",
                 "userText": "",
                 "dirText": "",
                 "envText": ""
                 }


def _create_state(state: ProfilerState, **kwargs: Optional[Any]) -> ProfilerState:
    return ProfilerState(**{**state._asdict(), **kwargs})


def handle_set_profiler_state(state: ProfilerState, action: Action) -> ProfilerState:
    return _create_state(state, entry={**action.payload})


def handle_set_profiler_output(state: ProfilerState, action: Action) -> ProfilerState:
    payload = cast(str, action.payload)
    return _create_state(state, output=payload)


def handle_set_profiler_analysis_file(state: ProfilerState, action: Action) -> ProfilerState:
    payload = cast(str, action.payload)
    return _create_state(state, file=payload)


def handle_clear_profiler_state(state: ProfilerState, *args) -> ProfilerState:
    return _create_state(state, entry=default_entry, output="")


def handle_profiler_init_state(state: ProfilerState, action: Action) -> ProfilerState:
    print("handle_profiler_init_state")
    return _create_state(state)


def handle_profiler_started_state(state: ProfilerState, action: Action) -> ProfilerState:
    print("handle_profiler_started_state")
    return _create_state(state, running=True)


def handle_profiler_done_state(state: ProfilerState, action: Action) -> ProfilerState:
    print("handle_profiler_done_state")
    return _create_state(state, running=False)


profiler_reducer: Reducer = handle_actions(
    {
        SET_PROFILER_STATE: handle_set_profiler_state,
        SET_PROFILER_OUTPUT: handle_set_profiler_output,
        SET_PROFILER_ANALYSIS_FILE: handle_set_profiler_analysis_file,
        CLEAR_PROFILER_STATE: handle_clear_profiler_state,
        PROFILING_INIT: handle_profiler_init_state,
        PROFILING_STARTED: handle_profiler_started_state,
        PROFILING_DONE: handle_profiler_done_state,
    },
    ProfilerState(entry=default_entry, output="", file="", running=False)
)
