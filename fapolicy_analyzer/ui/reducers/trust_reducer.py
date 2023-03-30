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

from typing import Any, NamedTuple, Optional, Sequence, Tuple, cast

from fapolicy_analyzer import Trust
from fapolicy_analyzer.redux import Action, Reducer, handle_actions
from fapolicy_analyzer.ui.actions import (
    ANCILLARY_TRUST_LOAD_COMPLETE,
    ANCILLARY_TRUST_LOAD_STARTED,
    ERROR_ANCILLARY_TRUST,
    ERROR_SYSTEM_TRUST,
    RECEIVED_ANCILLARY_TRUST_UPDATE,
    RECEIVED_SYSTEM_TRUST_UPDATE,
    REQUEST_ANCILLARY_TRUST,
    REQUEST_SYSTEM_TRUST,
    SYSTEM_TRUST_LOAD_COMPLETE,
    SYSTEM_TRUST_LOAD_STARTED,
)


class TrustState(NamedTuple):
    error: Optional[str]
    loading: bool
    percent_complete: int
    trust: Sequence[Trust]
    trust_count: int
    last_set_completed: Optional[Sequence[Trust]]
    timestamp: float


def _create_state(state: TrustState, **kwargs: Optional[Any]) -> TrustState:
    return TrustState(**{**state._asdict(), **kwargs})


def handle_request_trust(state: TrustState, _: Action) -> TrustState:
    return _create_state(state, loading=True, percent_complete=-1, error=None)


def handle_trust_load_started(state: TrustState, action: Action) -> TrustState:
    count, timestamp = cast(Tuple[int, float], action.payload)
    if timestamp < state.timestamp:
        return state

    return _create_state(
        state,
        loading=True,
        percent_complete=0,
        trust=[],
        last_set_completed=None,
        error=None,
        trust_count=count,
        timestamp=timestamp,
    )


def handle_received_trust_update(state: TrustState, action: Action) -> TrustState:
    update, running_count, timestamp = cast(
        Tuple[Sequence[Trust], int, float], action.payload
    )
    if timestamp < state.timestamp:
        return state

    #     print(
    #         f"""received trust update:
    # {os.linesep.join([u.path for u in update])}
    # """
    #     )
    return _create_state(
        state,
        percent_complete=running_count / state.trust_count * 100,
        trust=[*state.trust, *update],
        last_set_completed=update,
        error=None,
        timestamp=timestamp,
    )


def handle_trust_load_complete(state: TrustState, action: Action) -> TrustState:
    timestamp = cast(float, action.payload)
    if timestamp < state.timestamp:
        return state

    return _create_state(
        state, error=None, loading=False, last_set_completed=None, timestamp=timestamp
    )


def handle_error_trust(state: TrustState, action: Action) -> TrustState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload, loading=False)


system_trust_reducer: Reducer = handle_actions(
    {
        REQUEST_SYSTEM_TRUST: handle_request_trust,
        SYSTEM_TRUST_LOAD_STARTED: handle_trust_load_started,
        RECEIVED_SYSTEM_TRUST_UPDATE: handle_received_trust_update,
        SYSTEM_TRUST_LOAD_COMPLETE: handle_trust_load_complete,
        ERROR_SYSTEM_TRUST: handle_error_trust,
    },
    TrustState(
        error=None,
        trust=[],
        loading=False,
        percent_complete=-1,
        last_set_completed=None,
        trust_count=0,
        timestamp=0,
    ),
)

ancillary_trust_reducer: Reducer = handle_actions(
    {
        REQUEST_ANCILLARY_TRUST: handle_request_trust,
        ANCILLARY_TRUST_LOAD_STARTED: handle_trust_load_started,
        RECEIVED_ANCILLARY_TRUST_UPDATE: handle_received_trust_update,
        ANCILLARY_TRUST_LOAD_COMPLETE: handle_trust_load_complete,
        ERROR_ANCILLARY_TRUST: handle_error_trust,
    },
    TrustState(
        error=None,
        trust=[],
        loading=False,
        percent_complete=-1,
        last_set_completed=None,
        trust_count=0,
        timestamp=0,
    ),
)
