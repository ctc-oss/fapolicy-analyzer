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

from typing import Any, Dict, NamedTuple, Optional

from fapolicy_analyzer.redux import Action, Reducer, handle_actions
from fapolicy_analyzer.ui.actions import (
    CLEAR_PROFILER_STATE,
    PROFILING_EXEC,
    PROFILING_DONE,
    PROFILING_INIT,
    PROFILING_STARTED,
    PROFILING_KILL,
    PROFILING_TICK,
    SET_PROFILER_OUTPUT,
    START_PROFILING,
)


class ProfilerState(NamedTuple):
    cmd: Optional[str]
    pwd: Optional[str]
    env: Optional[str]
    uid: Optional[str]
    pid: Optional[int]
    duration: Optional[int]
    running: bool
    killing: bool
    events_log: Optional[str]
    stdout_log: Optional[str]
    stderr_log: Optional[str]


def _create_state(state: ProfilerState, **kwargs: Optional[Any]) -> ProfilerState:
    return ProfilerState(**{**state._asdict(), **kwargs})


def handle_start_profiling(state: ProfilerState, action: Action) -> ProfilerState:
    args: Dict[str, str] = action.payload
    uid = args.get("userText", None)
    pwd = args.get("dirText", None)
    env = args.get("envText", None)
    return _create_state(state, uid=uid, pwd=pwd, env=env)


def handle_set_profiler_output(state: ProfilerState, action: Action) -> ProfilerState:
    (ev, so, se) = action.payload
    return _create_state(state, events_log=ev, stdout_log=so, stderr_log=se)


def handle_clear_profiler_state(state: ProfilerState, action: Action) -> ProfilerState:
    return _create_state(state, cmd=None, pwd=None, env=None, uid=None, )


def handle_profiler_init_state(state: ProfilerState, action: Action) -> ProfilerState:
    return _create_state(state)


def handle_profiler_exec(state: ProfilerState, action: Action) -> ProfilerState:
    pid = action.payload
    return _create_state(state, pid=pid)


def handle_profiler_tick(state: ProfilerState, action: Action) -> ProfilerState:
    tick = action.payload
    return _create_state(state, duration=tick)


def handle_profiler_started_state(state: ProfilerState, action: Action) -> ProfilerState:
    cmd = action.payload
    return _create_state(state, cmd=cmd, running=True)


def handle_profiler_kill_state(state: ProfilerState, action: Action) -> ProfilerState:
    return _create_state(state, killing=True)


def handle_profiler_done_state(state: ProfilerState, action: Action) -> ProfilerState:
    return _create_state(state, running=False)


profiler_reducer: Reducer = handle_actions(
    {
        PROFILING_INIT: handle_profiler_init_state,
        SET_PROFILER_OUTPUT: handle_set_profiler_output,
        CLEAR_PROFILER_STATE: handle_clear_profiler_state,
        START_PROFILING: handle_start_profiling,
        PROFILING_STARTED: handle_profiler_started_state,
        PROFILING_EXEC: handle_profiler_exec,
        PROFILING_TICK: handle_profiler_tick,
        PROFILING_DONE: handle_profiler_done_state,
        PROFILING_KILL: handle_profiler_kill_state,
    },
    ProfilerState(cmd=None,
                  pwd=None,
                  env=None,
                  uid=None,
                  pid=None,
                  duration=None,
                  running=False,
                  killing=False,
                  events_log=None,
                  stdout_log=None,
                  stderr_log=None, )
)
