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

from typing import Any, NamedTuple, Optional, Sequence, cast

from fapolicy_analyzer import Rule
from fapolicy_analyzer.ui.actions import ERROR_RULES, RECEIVED_RULES, REQUEST_RULES
from fapolicy_analyzer.redux import Action, Reducer, handle_actions


class RuleState(NamedTuple):
    error: Optional[str]
    loading: bool
    rules: Sequence[Rule]


def _create_state(state: RuleState, **kwargs: Optional[Any]) -> RuleState:
    return RuleState(**{**state._asdict(), **kwargs})


def handle_request_rules(state: RuleState, action: Action) -> RuleState:
    return _create_state(state, loading=True, error=None)


def handle_received_rules(state: RuleState, action: Action) -> RuleState:
    payload = cast(Sequence[Rule], action.payload)
    return _create_state(state, rules=payload, error=None, loading=False)


def handle_error_rules(state: RuleState, action: Action) -> RuleState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload, loading=False)


rule_reducer: Reducer = handle_actions(
    {
        REQUEST_RULES: handle_request_rules,
        RECEIVED_RULES: handle_received_rules,
        ERROR_RULES: handle_error_rules,
    },
    RuleState(error=None, rules=[], loading=False),
)
