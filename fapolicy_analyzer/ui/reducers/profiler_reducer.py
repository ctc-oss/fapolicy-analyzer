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
    PROFILER_CLEAR_STATE_CMD,
    PROFILING_INIT_EVENT,
    PROFILER_SET_OUTPUT_CMD,
    START_PROFILING_REQUEST,
    START_PROFILING_RESPONSE,
    PROFILING_KILL_RESPONSE,
    PROFILING_DONE_EVENT,
    PROFILING_TICK_EVENT,
    PROFILING_EXEC_EVENT,
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


class ProfilerStarted(ProfilerState):
    pass


class ProfilerTick(ProfilerState):
    pass


class ProfilerKill(ProfilerState):
    pass


class ProfilerDone(ProfilerState):
    pass


def _create_state(target, source: ProfilerState, **kwargs: Optional[Any]) -> ProfilerState:
    return target(**{**source._asdict(), **kwargs})


def handle_profiler_init_state(state: ProfilerState, action: Action) -> ProfilerState:
    return _create_state(ProfilerState, state)


def handle_start_profiling_request(state: ProfilerState, action: Action) -> ProfilerState:
    args: Dict[str, str] = action.payload
    uid = args.get("uid", None)
    pwd = args.get("pwd", None)
    env = args.get("env_dict", None)
    return _create_state(ProfilerState, state, uid=uid, pwd=pwd, env=env)


def handle_start_profiling_response(state: ProfilerState, action: Action) -> ProfilerState:
    cmd = action.payload
    return _create_state(ProfilerState, state, cmd=cmd, running=True)


def handle_set_profiler_output(state: ProfilerState, action: Action) -> ProfilerState:
    (ev, so, se) = action.payload
    return _create_state(ProfilerState, state, events_log=ev, stdout_log=so, stderr_log=se)


def handle_clear_profiler_state(state: ProfilerState, action: Action) -> ProfilerState:
    return _create_state(ProfilerState, state, cmd=None, pwd=None, env=None, uid=None, )


def handle_profiler_exec(state: ProfilerState, action: Action) -> ProfilerState:
    pid = action.payload
    return _create_state(ProfilerStarted, state, pid=pid)


def handle_profiler_tick(state: ProfilerState, action: Action) -> ProfilerState:
    tick = action.payload
    return _create_state(ProfilerTick, state, duration=tick)


def handle_profiler_kill(state: ProfilerState, action: Action) -> ProfilerState:
    return _create_state(ProfilerKill, state, killing=True)


def handle_profiler_done(state: ProfilerState, action: Action) -> ProfilerState:
    return _create_state(ProfilerDone, state, running=False)


profiler_reducer: Reducer = handle_actions(
    {
        PROFILING_INIT_EVENT: handle_profiler_init_state,
        PROFILER_SET_OUTPUT_CMD: handle_set_profiler_output,
        PROFILER_CLEAR_STATE_CMD: handle_clear_profiler_state,
        START_PROFILING_REQUEST: handle_start_profiling_request,
        START_PROFILING_RESPONSE: handle_start_profiling_response,
        PROFILING_EXEC_EVENT: handle_profiler_exec,
        PROFILING_TICK_EVENT: handle_profiler_tick,
        PROFILING_DONE_EVENT: handle_profiler_done,
        PROFILING_KILL_RESPONSE: handle_profiler_kill,
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
