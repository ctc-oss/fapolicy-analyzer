from time import sleep
from typing import Callable, cast

from fapolicy_analyzer import *
from fapolicy_analyzer.redux import (
    Action,
    ReduxFeatureModule,
    combine_epics,
    create_feature_module,
    of_init_feature,
    of_type, create_store, select_feature, combine_reducers, Reducer, handle_actions,
)
from fapolicy_analyzer.ui.actions import (
    REQUEST_ANCILLARY_TRUST,
    REQUEST_SYSTEM_TRUST,
    error_ancillary_trust,
    error_system_trust,
    init_system,
    received_ancillary_trust,
    received_system_trust,
    system_received, request_system_trust, SYSTEM_RECEIVED, request_ancillary_trust,
)
from fapolicy_analyzer.ui.features import SYSTEM_FEATURE
from rx import of, pipe, operators
from rx.operators import catch, map

from fapolicy_analyzer.ui.reducers.ancillary_trust_reducer import ancillary_trust_reducer
from fapolicy_analyzer.ui.reducers.system_reducer import SystemState, _create_state
from fapolicy_analyzer.ui.reducers.system_trust_reducer import system_trust_reducer


def handle_system_received(state: SystemState, action: Action) -> SystemState:
    payload = cast(System, action.payload)
    return _create_state(state, system=payload)


my_system_reducer: Reducer = combine_reducers(
    {
        "system": handle_actions(
            {
                SYSTEM_RECEIVED: handle_system_received,
            },
            SystemState(error=None, system=None, checkpoint=None, deployed=False),
        ),
        "ancillary_trust": ancillary_trust_reducer,
        "system_trust": system_trust_reducer,
    }
)


def create_system_feature(
        dispatch: Callable, _system: System = None, _apply_changesets=None) -> ReduxFeatureModule:

    def _init_system() -> Action:
        print("_init_system")
        dispatch(system_received(_system))
        return init_system()

    def _get_ancillary_trust(_: Action) -> Action:
        print("_get_ancillary_trust")
        trust = _system.ancillary_trust()
        return received_ancillary_trust(trust)

    def _get_system_trust(_: Action) -> Action:
        print("_get_system_trust")
        trust = _system.system_trust()
        return received_system_trust(trust)

    init_epic = pipe(
        of_init_feature(SYSTEM_FEATURE),
        map(lambda _: _init_system()),
    )

    request_ancillary_trust_epic = pipe(
        of_type(REQUEST_ANCILLARY_TRUST),
        map(_get_ancillary_trust),
        catch(lambda ex, source: of(error_ancillary_trust(str(ex)))),
    )

    request_system_trust_epic = pipe(
        of_type(REQUEST_SYSTEM_TRUST),
        map(_get_system_trust),
        catch(lambda ex, source: of(error_system_trust(str(ex)))),
    )

    system_epic = combine_epics(
        init_epic,
        request_ancillary_trust_epic,
        request_system_trust_epic,
    )

    return create_feature_module(SYSTEM_FEATURE, my_system_reducer, epic=system_epic)


def handle_response(state):
    print(state)
    print(f"found {len(state.get('system').system.system_trust())} system trust entries")


def system_error(e):
    print(f"system error: {e}")


def available(updates):
    print(f"updated trust available:")
    for trust in updates:
        print(f"\t{trust}")


def completed():
    print(f"trust checking completed")


s1 = System()
check_disk_trust(s1, available, completed)

sleep(1000)

# store = create_store()
# store.add_feature_module(create_system_feature(store.dispatch, s1))
#
# f = store.as_observable().pipe(operators.map(select_feature(SYSTEM_FEATURE)))
# f.subscribe(
#     on_next=handle_response,
#     on_error=system_error,
#     on_completed=None,
# )
#
#
# def call_back():
#     print("called back")
#     store.dispatch(request_system_trust())
#
#
# s1.install_trust_callback(call_back)
# s1.call_trust_callback()
#
# # store.dispatch(request_system_trust())
