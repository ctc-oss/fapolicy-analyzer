from functools import partial
from typing import Callable, Dict, Tuple

import gi
from rx import of
from rx.core.pipe import pipe
from rx.operators import catch, map

from fapolicy_analyzer import Profiler, ExecHandle, ProcHandle
from fapolicy_analyzer.redux import (
    Action,
)
from fapolicy_analyzer.redux import create_feature_module, ReduxFeatureModule, of_init_feature, combine_epics, of_type
from fapolicy_analyzer.ui.actions import error_profiling, START_PROFILING, profiler_init, profiling_started, profiler_done, PROFILING_KILL, terminating_profiler, profiler_tick, profiler_exec, \
    set_profiler_output
from fapolicy_analyzer.ui.reducers import profiler_reducer

gi.require_version("Gtk", "3.0")
from gi.repository import GLib  # isort: skip

PROFILING_FEATURE = "profiling"
_handle: ProcHandle


def create_profiler_feature(
        dispatch: Callable
) -> ReduxFeatureModule:
    profiler_active: bool = False

    def _idle_dispatch(action: Action):
        GLib.idle_add(dispatch, action)

    def _init_profiler() -> Action:
        return profiler_init()

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

        print("=========== starting profiling =============")

        # profiler backend
        p = Profiler()

        # session args
        args: Dict[str, str] = action.payload

        # target command

        target = args.get("executeText", None)
        target_args = args.get("argText", None)
        cmd = target if target else None
        if cmd and target_args:
            cmd = f"{target} {target_args}"

        # set user, pwd, envs
        p.user = args.get("userText", None)
        p.pwd = args.get("dirText", None)
        p.env = args.get("envDict", None)

        # set callbacks
        p.exec_callback = exed
        p.tick_callback = tick
        p.done_callback = done

        # execute and dispatch
        _handle = p.profile(cmd)
        return profiling_started(cmd)

    def _kill_profiler(action: Action) -> Action:
        global _handle
        nonlocal profiler_active

        if not profiler_active:
            return action

        _handle.kill()

        return terminating_profiler()

    init_epic = pipe(
        of_init_feature(PROFILING_FEATURE),
        map(lambda _: _init_profiler()),
    )

    start_profiling_epic = pipe(
        of_type(START_PROFILING),
        map(_start_profiling),
        catch(lambda e, source: of(error_profiling(str(e))))
    )

    kill_profiler_epic = pipe(
        of_type(PROFILING_KILL),
        map(_kill_profiler),
        catch(lambda e, source: of(error_profiling(str(e))))
    )

    profiler_epic = combine_epics(
        init_epic,
        start_profiling_epic,
        kill_profiler_epic,
    )

    return create_feature_module(PROFILING_FEATURE, profiler_reducer, epic=profiler_epic)
