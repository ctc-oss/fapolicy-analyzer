# Copyright Concurrent Technologies Corporation 2023
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
from functools import partial
from typing import Callable, Dict

import gi
from rx import of
from rx.core.pipe import pipe
from rx.operators import catch, map

from fapolicy_analyzer import Profiler, ExecHandle, ProcHandle
from fapolicy_analyzer.redux import (
    Action,
)
from fapolicy_analyzer.redux import (
    create_feature_module,
    ReduxFeatureModule,
    combine_epics,
    of_type
)
from fapolicy_analyzer.ui.actions import (
    profiling_started,
    profiler_done,
    terminating_profiler,
    profiler_tick,
    profiler_exec,
    set_profiler_output,
    profiler_execution_error,
    profiler_initialization_error,
    START_PROFILING_REQUEST,
    PROFILING_KILL_REQUEST,
    profiler_termination_error
)
from fapolicy_analyzer.ui.reducers import profiler_reducer
from fapolicy_analyzer.ui.strings import PROFILER_EXEC_ERROR, PROFILER_INIT_ERROR

gi.require_version("Gtk", "3.0")
from gi.repository import GLib  # isort: skip

PROFILING_FEATURE = "profiling"
_handle: ProcHandle


def create_profiler_feature(dispatch: Callable) -> ReduxFeatureModule:
    profiler_active: bool = False

    def _idle_dispatch(action: Action):
        GLib.idle_add(dispatch, action)

    def _on_exec(h: ExecHandle, action_fn: Callable[[int], Action]):
        _idle_dispatch(action_fn(h.pid))
        _idle_dispatch(set_profiler_output(h.event_log, h.stdout_log, h.stderr_log))

    def _on_tick(_: ExecHandle, duration: int, action_fn: Callable[[int], Action]):
        _idle_dispatch(action_fn(duration))

    def _on_done(action_fn: Callable[[], Action], flag_fn: Callable[[], None]):
        _idle_dispatch(action_fn())
        flag_fn()

    def _start_profiling(action: Action) -> Action:
        global _handle
        nonlocal profiler_active

        def on_done():
            nonlocal profiler_active
            profiler_active = False

        if profiler_active:
            return action

        profiler_active = True

        exed = partial(
            _on_exec,
            action_fn=profiler_exec,
        )

        tick = partial(
            _on_tick,
            action_fn=profiler_tick,
        )

        done = partial(
            _on_done,
            action_fn=profiler_done,
            flag_fn=on_done,
        )

        # build target command from session args
        args: Dict[str, str] = action.payload
        target = args.get("cmd", None)
        target_args = args.get("arg", None)
        cmd = target if target else None
        if cmd and target_args:
            cmd = f"{target} {target_args}"

        # configure the backend
        try:
            p = Profiler()

            # set callbacks
            p.exec_callback = exed
            p.tick_callback = tick
            p.done_callback = done

            # set user, pwd, envs
            p.user = args.get("uid", None)
            p.pwd = args.get("pwd", None)
            p.env = args.get("env", None)
        except RuntimeError:
            dispatch(profiler_initialization_error(PROFILER_INIT_ERROR))
            return profiler_done()

        # execute and dispatch
        try:
            _handle = p.profile(cmd)
        except RuntimeError:
            dispatch(profiler_execution_error(PROFILER_EXEC_ERROR))
            return profiler_done()

        return profiling_started(cmd)

    def _kill_profiler(action: Action) -> Action:
        global _handle
        nonlocal profiler_active

        if not profiler_active:
            return action

        _handle.kill()

        return terminating_profiler()

    start_profiling_epic = pipe(
        of_type(START_PROFILING_REQUEST),
        map(_start_profiling),
        catch(lambda e, source: of(profiler_initialization_error(str(e))))
    )

    kill_profiler_epic = pipe(
        of_type(PROFILING_KILL_REQUEST),
        map(_kill_profiler),
        catch(lambda e, source: of(profiler_termination_error(str(e))))
    )

    profiler_epic = combine_epics(
        start_profiling_epic,
        kill_profiler_epic,
    )

    return create_feature_module(PROFILING_FEATURE, profiler_reducer, epic=profiler_epic)
