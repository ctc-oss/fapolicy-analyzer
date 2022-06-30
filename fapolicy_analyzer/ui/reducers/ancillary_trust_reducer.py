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
    ADD_CHANGESETS,
    ANCILLARY_TRUST_DEPLOYED,
    CLEAR_CHANGESETS,
    ERROR_ANCILLARY_TRUST,
    ERROR_DEPLOYING_ANCILLARY_TRUST,
    RECEIVED_ANCILLARY_TRUST,
    REQUEST_ANCILLARY_TRUST,
)
from fapolicy_analyzer.redux import Action, Reducer, handle_actions


class TrustState(NamedTuple):
    error: Optional[str]
    loading: bool
    trust: Sequence[Trust]
    deployed: bool


def _create_state(state: TrustState, **kwargs: Optional[Any]) -> TrustState:
    return TrustState(**{**state._asdict(), **kwargs})


def handle_request_ancillary_trust(state: TrustState, action: Action) -> TrustState:
    return _create_state(state, loading=True, error=None)


def handle_received_ancillary_trust(state: TrustState, action: Action) -> TrustState:
    payload = cast(Sequence[Trust], action.payload)
    return _create_state(state, trust=payload, error=None, loading=False)


def handle_error_ancillary_trust(state: TrustState, action: Action) -> TrustState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload, loading=False)


def handle_ancillary_trust_deployed(state: TrustState, action: Action) -> TrustState:
    return _create_state(state, error=None, deployed=True)


def handle_error_deploying_ancillary_trust(
    state: TrustState, action: Action
) -> TrustState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload)


def handle_add_changesets(state: TrustState, action: Action) -> TrustState:
    return _create_state(state, error=None, deployed=False)


def handle_clear_changesets(state: TrustState, action: Action) -> TrustState:
    return _create_state(state, error=None, deployed=True)


ancillary_trust_reducer: Reducer = handle_actions(
    {
        REQUEST_ANCILLARY_TRUST: handle_request_ancillary_trust,
        RECEIVED_ANCILLARY_TRUST: handle_received_ancillary_trust,
        ERROR_ANCILLARY_TRUST: handle_error_ancillary_trust,
        ANCILLARY_TRUST_DEPLOYED: handle_ancillary_trust_deployed,
        ERROR_DEPLOYING_ANCILLARY_TRUST: handle_error_deploying_ancillary_trust,
        ADD_CHANGESETS: handle_add_changesets,
        CLEAR_CHANGESETS: handle_clear_changesets,
    },
    TrustState(error=None, trust=[], deployed=True, loading=False),
)
