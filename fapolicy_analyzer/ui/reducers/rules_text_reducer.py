# Copyright Concurrent Technologies Corporation 2022
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

from typing import Any, NamedTuple, Optional, cast

from fapolicy_analyzer.ui.actions import (
    ERROR_RULES_TEXT,
    RECEIVED_RULES_TEXT,
    REQUEST_RULES_TEXT,
)
from redux import Action, Reducer, handle_actions


class RulesTextState(NamedTuple):
    error: Optional[str]
    loading: bool
    rules_text: str


def _create_state(state: RulesTextState, **kwargs: Optional[Any]) -> RulesTextState:
    return RulesTextState(**{**state._asdict(), **kwargs})


def handle_request_rules_text(state: RulesTextState, _: Action) -> RulesTextState:
    return _create_state(state, loading=True, error=None)


def handle_received_rules_text(state: RulesTextState, action: Action) -> RulesTextState:
    payload = cast(str, action.payload)
    return _create_state(state, rules_text=payload, error=None, loading=False)


def handle_error_rules_text(state: RulesTextState, action: Action) -> RulesTextState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload, loading=False)


rules_text_reducer: Reducer = handle_actions(
    {
        REQUEST_RULES_TEXT: handle_request_rules_text,
        RECEIVED_RULES_TEXT: handle_received_rules_text,
        ERROR_RULES_TEXT: handle_error_rules_text,
    },
    RulesTextState(error=None, rules_text={}, loading=False),
)
