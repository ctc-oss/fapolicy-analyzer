from fapolicy_analyzer.ui.actions import SYSTEM_INITIALIZED
from fapolicy_analyzer.redux import Reducer, combine_reducers, handle_actions
from .ancillary_trust_reducer import ancillary_trust_reducer
from .changeset_reducer import changeset_reducer
from .event_reducer import event_reducer
from .group_reducer import group_reducer
from .system_trust_reducer import system_trust_reducer
from .user_reducer import user_reducer


system_initialized_reducer: Reducer = handle_actions(
    {SYSTEM_INITIALIZED: lambda *_: True}, False
)

system_reducer: Reducer = combine_reducers(
    {
        "initialized": system_initialized_reducer,
        "ancillary_trust": ancillary_trust_reducer,
        "changesets": changeset_reducer,
        "events": event_reducer,
        "groups": group_reducer,
        "system_trust": system_trust_reducer,
        "users": user_reducer,
    }
)
