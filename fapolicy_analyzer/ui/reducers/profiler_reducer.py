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

#
# About these state subtypes:
# I am using these subclasses to tag the event type, which allows
# subscribers to route handling by type of the state received.
# could also achieve this by adding the action type string to the
# state but wanted to see what this looks like and how it holds up.
# I wanted to also separate the properties into proper contexts by type
# but that proves troublesome on some transitions, you still end up
# having to include properties that are not applicable, just for the
# next transition. Originally there were subtypes for each possible
# state, but currently there are only subtypes for the states that need
# special handling, all other cases use the base class ProfilerState.
#
# In summary, this approach wanted to behave like a State Machine, but didnt quite succeed.
#


class ProfilerStarted(ProfilerState):
    pass


class ProfilerTick(ProfilerState):
    pass


class ProfilerKill(ProfilerState):
    pass


class ProfilerDone(ProfilerState):
    pass


def empty_profiler_state():
    return ProfilerState(cmd=None,
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


def derive_profiler_state(target, source: ProfilerState, **kwargs: Optional[Any]) -> ProfilerState:
    return target(**{**source._asdict(), **kwargs})


def profiler_state(target, **kwargs: Optional[Any]) -> ProfilerState:
    return target(**{**empty_profiler_state()._asdict(), **kwargs})


def handle_profiler_init_state(state: ProfilerState, action: Action) -> ProfilerState:
    return derive_profiler_state(ProfilerState, state)


def handle_start_profiling_request(state: ProfilerState, action: Action) -> ProfilerState:
    args: Dict[str, str] = action.payload
    uid = args.get("uid", None)
    pwd = args.get("pwd", None)
    env = args.get("env_dict", None)
    return derive_profiler_state(ProfilerState, state, uid=uid, pwd=pwd, env=env)


def handle_start_profiling_response(state: ProfilerState, action: Action) -> ProfilerState:
    cmd = action.payload
    return derive_profiler_state(ProfilerState, state, cmd=cmd, running=True)


def handle_set_profiler_output(state: ProfilerState, action: Action) -> ProfilerState:
    (ev, so, se) = action.payload
    return derive_profiler_state(ProfilerState, state, events_log=ev, stdout_log=so, stderr_log=se)


def handle_clear_profiler_state(state: ProfilerState, action: Action) -> ProfilerState:
    return derive_profiler_state(ProfilerState, state, cmd=None, pwd=None, env=None, uid=None, )


def handle_profiler_exec(state: ProfilerState, action: Action) -> ProfilerState:
    pid = action.payload
    return derive_profiler_state(ProfilerStarted, state, pid=pid)


def handle_profiler_tick(state: ProfilerState, action: Action) -> ProfilerState:
    tick = action.payload
    return derive_profiler_state(ProfilerTick, state, duration=tick)


def handle_profiler_kill(state: ProfilerState, action: Action) -> ProfilerState:
    return derive_profiler_state(ProfilerKill, state, killing=True)


def handle_profiler_done(state: ProfilerState, action: Action) -> ProfilerState:
    return derive_profiler_state(ProfilerDone, state, running=False)


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
    empty_profiler_state()
)
