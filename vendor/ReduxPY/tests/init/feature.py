from typing import Any
from rx import Observable, pipe
from rx.operators import do_action, filter, map, ignore_elements

from redux import (
    Epic,
    Reducer,
    ReduxFeatureModule,
    combine_epics,
    create_action,
    create_feature_module,
    handle_actions,
    of_init_feature,
    of_type,
    select_action_payload,
    select_feature,
    StateType,
    Action,
)

INIT_FEATURE = "INIT_FEATURE"

ADD_INIT_ACTION = "ADD_INIT_ACTION"

add_init_action = create_action(ADD_INIT_ACTION)
select_init_feature_module = select_feature(INIT_FEATURE)


def create_init_feature() -> ReduxFeatureModule:
    """
        Constructs a new sample feature
    """

    def handle_init_action(state: Any, action: Action) -> Any:
        return select_action_payload(action)

    sample_reducer = handle_actions({ADD_INIT_ACTION: handle_init_action})

    add_epic = pipe(of_type(ADD_INIT_ACTION), ignore_elements(),)

    init_epic = pipe(
        of_init_feature(INIT_FEATURE), map(lambda x: add_init_action("init")),
    )

    sample_epic = combine_epics(add_epic, init_epic)

    return create_feature_module(INIT_FEATURE, sample_reducer, sample_epic)

