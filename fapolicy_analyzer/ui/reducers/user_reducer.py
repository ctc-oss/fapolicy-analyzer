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

from fapolicy_analyzer import User
from fapolicy_analyzer.ui.actions import ERROR_USERS, RECEIVED_USERS, REQUEST_USERS
from fapolicy_analyzer.redux import Action, Reducer, handle_actions


class UserState(NamedTuple):
    error: Optional[str]
    loading: bool
    users: Sequence[User]


def _create_state(state: UserState, **kwargs: Optional[Any]) -> UserState:
    return UserState(**{**state._asdict(), **kwargs})


def handle_request_users(state: UserState, action: Action) -> UserState:
    return _create_state(state, loading=True, error=None)


def handle_received_users(state: UserState, action: Action) -> UserState:
    payload = cast(Sequence[User], action.payload)
    return _create_state(state, users=payload, error=None, loading=False)


def handle_error_users(state: UserState, action: Action) -> UserState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload, loading=False)


user_reducer: Reducer = handle_actions(
    {
        REQUEST_USERS: handle_request_users,
        RECEIVED_USERS: handle_received_users,
        ERROR_USERS: handle_error_users,
    },
    UserState(error=None, users=[], loading=False),
)
