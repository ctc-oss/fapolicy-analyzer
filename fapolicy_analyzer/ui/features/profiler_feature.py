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
from fapolicy_analyzer.ui.actions import error_profiling, START_PROFILING, profiler_init, profiling_started, profiler_done, PROFILING_KILL, terminating_profiler, profiler_tick
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

    def _on_tick(h: ExecHandle, duration: int, action_fn: Callable[[Tuple[int, int]], Action]):
        update = (h.pid, duration)
        _idle_dispatch(action_fn(update))

    def _on_done(action_fn: Callable[[], Action], flag_fn: Callable[[], None]):
        print("****** profiling done ******")
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

        args: Dict[str, str] = action.payload
        target = args.get("executeText", "")
        target_args = args.get("argText", "")

        p = Profiler()
        p.tick_callback = tick
        p.done_callback = done
        cmd = f"{target} {target_args}"
        _handle = p.profile(cmd)

        return profiling_started(cmd)

    def _kill_profiler(action: Action) -> Action:
        global _handle
        nonlocal profiler_active

        if not profiler_active:
            return action

        print("-------- terminating profiler ----------")

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
