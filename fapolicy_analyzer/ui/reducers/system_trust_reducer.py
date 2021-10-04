from fapolicy_analyzer import Trust
from redux import Action, Reducer, handle_actions
from typing import Any, NamedTuple, Optional, Sequence, cast
from fapolicy_analyzer.ui.actions import (
    RECEIVED_SYSTEM_TRUST,
    ERROR_SYSTEM_TRUST,
)


class TrustState(NamedTuple):
    error: str
    trust: Sequence[Trust]


def _create_state(state: TrustState, **kwargs: Optional[Any]) -> TrustState:
    return TrustState(**{**state._asdict(), **kwargs})


def handle_received_system_trust(state: TrustState, action: Action) -> TrustState:
    payload = cast(Sequence[Trust], action.payload)
    return _create_state(state, trust=payload, error=None)


def handle_error_system_trust(state: TrustState, action: Action) -> TrustState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload)


system_trust_reducer: Reducer = handle_actions(
    {
        RECEIVED_SYSTEM_TRUST: handle_received_system_trust,
        ERROR_SYSTEM_TRUST: handle_error_system_trust,
    },
    TrustState(error=None, trust=[]),
)
