from fapolicy_analyzer.ui.actions import (
    ERROR_EVENTS,
    RECEIVED_EVENTS,
    REQUEST_EVENTS,
)
from fapolicy_analyzer import EventLog
from fapolicy_analyzer.redux import Action, Reducer, handle_actions
from typing import Any, NamedTuple, Optional, Sequence, cast


class EventState(NamedTuple):
    error: str
    loading: bool
    log: Sequence[EventLog]


def _create_state(state: EventState, **kwargs: Optional[Any]) -> EventState:
    return EventState(**{**state._asdict(), **kwargs})


def handle_request_events(state: EventState, action: Action) -> EventState:
    return _create_state(state, loading=True, error=None)


def handle_received_events(state: EventState, action: Action) -> EventState:
    payload = cast(Sequence[EventLog], action.payload)
    return _create_state(state, log=payload, error=None, loading=False)


def handle_error_events(state: EventState, action: Action) -> EventState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload, loading=False)


event_reducer: Reducer = handle_actions(
    {
        REQUEST_EVENTS: handle_request_events,
        RECEIVED_EVENTS: handle_received_events,
        ERROR_EVENTS: handle_error_events,
    },
    EventState(error=None, log=None, loading=False),
)
