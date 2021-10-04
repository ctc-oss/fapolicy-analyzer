from redux import Reducer, combine_reducers
from .ancillary_trust_reducer import ancillary_trust_reducer
from .changeset_reducer import changeset_reducer
from .event_reducer import event_reducer
from .group_reducer import group_reducer
from .system_trust_reducer import system_trust_reducer
from .user_reducer import user_reducer

system_reducer: Reducer = combine_reducers(
    {
        "ancillary_trust": ancillary_trust_reducer,
        "changesets": changeset_reducer,
        "events": event_reducer,
        "groups": group_reducer,
        "system_trust": system_trust_reducer,
        "users": user_reducer,
    }
)
