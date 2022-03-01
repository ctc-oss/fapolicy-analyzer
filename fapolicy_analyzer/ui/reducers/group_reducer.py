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

from fapolicy_analyzer import Group
from fapolicy_analyzer.ui.actions import ERROR_GROUPS, RECEIVED_GROUPS, REQUEST_GROUPS
from redux import Action, Reducer, handle_actions


class GroupState(NamedTuple):
    error: Optional[str]
    loading: bool
    groups: Sequence[Group]


def _create_state(state: GroupState, **kwargs: Optional[Any]) -> GroupState:
    return GroupState(**{**state._asdict(), **kwargs})


def handle_request_groups(state: GroupState, action: Action) -> GroupState:
    return _create_state(state, loading=True, error=None)


def handle_received_groups(state: GroupState, action: Action) -> GroupState:
    payload = cast(Sequence[Group], action.payload)
    return _create_state(state, groups=payload, error=None, loading=False)


def handle_error_groups(state: GroupState, action: Action) -> GroupState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload, loading=False)


group_reducer: Reducer = handle_actions(
    {
        REQUEST_GROUPS: handle_request_groups,
        RECEIVED_GROUPS: handle_received_groups,
        ERROR_GROUPS: handle_error_groups,
    },
    GroupState(error=None, groups=[], loading=False),
)
