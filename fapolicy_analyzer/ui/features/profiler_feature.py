from fapolicy_analyzer.ui.actions import init_profiler
from fapolicy_analyzer.ui.reducers import profiler_reducer
from fapolicy_analyzer.redux import create_feature_module, ReduxFeatureModule, of_init_feature, combine_epics

from functools import partial
from typing import Callable, Sequence, Tuple, Dict

from rx import of
from rx.core.pipe import pipe
from rx.operators import catch, filter, map

from fapolicy_analyzer.redux import (
    Action,
)

PROFILING_FEATURE = "profiling"


def create_profiler_feature(
        dispatch: Callable
) -> ReduxFeatureModule:

    def _init_profiler() -> Action:
        print("=========== initializing profiler feature ===========")
        return init_profiler()


    init_epic = pipe(
        of_init_feature(PROFILING_FEATURE),
        map(lambda _: _init_profiler()),
    )

    profiler_epic = combine_epics(
        init_epic,
    )

    return create_feature_module(PROFILING_FEATURE, profiler_reducer, epic=profiler_epic)
