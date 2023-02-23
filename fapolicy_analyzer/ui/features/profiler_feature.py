from functools import partial
from typing import Callable

import gi
from rx import of
from rx.core.pipe import pipe
from rx.operators import catch, map

from fapolicy_analyzer import Profiler
from fapolicy_analyzer.redux import (
    Action,
)
from fapolicy_analyzer.redux import create_feature_module, ReduxFeatureModule, of_init_feature, combine_epics, of_type
from fapolicy_analyzer.ui.actions import error_profiling, START_PROFILING, profiler_init, profiling_started, profiler_done
from fapolicy_analyzer.ui.reducers import profiler_reducer

gi.require_version("Gtk", "3.0")
from gi.repository import GLib  # isort: skip

PROFILING_FEATURE = "profiling"
_profiler: Profiler


def create_profiler_feature(
        dispatch: Callable
) -> ReduxFeatureModule:
    profiler_active: bool = False

    def _idle_dispatch(action: Action):
        GLib.idle_add(dispatch, action)

    def _init_profiler() -> Action:
        print("=========== initializing profiler feature ===========")
        return profiler_init()

    def _on_done(action_fn: Callable[[], Action], flag_fn: Callable[[], None]):
        print("****** profiling done ******")
        _idle_dispatch(action_fn())
        flag_fn()

    def _start_profiling(action: Action) -> Action:
        nonlocal profiler_active

        def on_done():
            nonlocal profiler_active
            profiler_active = False

        if profiler_active:
            return action

        profiler_active = True

        done = partial(
            _on_done,
            action_fn=profiler_done,
            flag_fn=on_done,
        )

        print("=========== starting profiling =============")
        # todo-redux;; this is where the profiler is kicked off
        #              for now just going to simulate the exec event
        #              but eventually that will be from the execd callback
        p = Profiler()
        p.done_callback = done
        p.profile("ls /tmp")

        return profiling_started()

    init_epic = pipe(
        of_init_feature(PROFILING_FEATURE),
        map(lambda _: _init_profiler()),
    )

    start_profiling_epic = pipe(
        of_type(START_PROFILING),
        map(_start_profiling),
        catch(lambda e, source: of(error_profiling(str(e))))
    )

    profiler_epic = combine_epics(
        init_epic,
        start_profiling_epic,
    )

    return create_feature_module(PROFILING_FEATURE, profiler_reducer, epic=profiler_epic)
