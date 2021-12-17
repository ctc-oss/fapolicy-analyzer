# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
#
#
# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
from fapolicy_analyzer.ui.actions import (
    ERROR_EVENTS,
    RECEIVED_EVENTS,
    REQUEST_EVENTS,
)
from fapolicy_analyzer import EventLog
from redux import Action, Reducer, handle_actions
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
