# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Any, NamedTuple, Optional, Sequence, cast

from fapolicy_analyzer import Trust
from fapolicy_analyzer.ui.actions import (
    ERROR_SYSTEM_TRUST,
    RECEIVED_SYSTEM_TRUST,
    REQUEST_SYSTEM_TRUST,
    SIGNAL_TRUST_RELOAD,
)
from fapolicy_analyzer.redux import Action, Reducer, handle_actions


class TrustState(NamedTuple):
    error: Optional[str]
    loading: bool
    trust: Sequence[Trust]
    signal_reload: bool


def _create_state(state: TrustState, **kwargs: Optional[Any]) -> TrustState:
    return TrustState(**{**state._asdict(), **kwargs})


def handle_request_system_trust(state: TrustState, action: Action) -> TrustState:
    return _create_state(state, loading=True, error=None)


def handle_received_system_trust(state: TrustState, action: Action) -> TrustState:
    payload = cast(Sequence[Trust], action.payload)
    return _create_state(state, trust=payload, error=None, loading=False)


def handle_error_system_trust(state: TrustState, action: Action) -> TrustState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload, loading=False)


def handle_signal_trust_reload(state: TrustState, action: Action) -> TrustState:
    return _create_state(state, loading=True, error=None, signal_reload=True)


system_trust_reducer: Reducer = handle_actions(
    {
        REQUEST_SYSTEM_TRUST: handle_request_system_trust,
        RECEIVED_SYSTEM_TRUST: handle_received_system_trust,
        ERROR_SYSTEM_TRUST: handle_error_system_trust,
        SIGNAL_TRUST_RELOAD: handle_signal_trust_reload,
    },
    TrustState(error=None, trust=[], loading=False, signal_reload=False),
)
