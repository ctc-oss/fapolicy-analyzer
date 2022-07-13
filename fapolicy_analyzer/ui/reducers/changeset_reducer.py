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

from fapolicy_analyzer.ui.actions import (
    ADD_CHANGESETS,
    CLEAR_CHANGESETS,
    ERROR_APPLY_CHANGESETS,
)
from fapolicy_analyzer.ui.changeset_wrapper import Changeset
from redux import Action, Reducer, handle_actions


class ChangesetState(NamedTuple):
    error: Optional[str]
    changesets: Sequence[Changeset]


def _create_state(state: ChangesetState, **kwargs: Optional[Any]) -> ChangesetState:
    return ChangesetState(**{**state._asdict(), **kwargs})


def handle_add_changesets(state: ChangesetState, action: Action) -> ChangesetState:
    payload = cast(Sequence[Changeset], action.payload)
    return _create_state(state, error=None, changesets=[*state.changesets, *payload])


def handle_error_apply_changesets(
    state: ChangesetState, action: Action
) -> ChangesetState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload)


def handle_clear_changesets(state: ChangesetState, action: Action) -> ChangesetState:
    return _create_state(state, changesets=[])


changeset_reducer: Reducer = handle_actions(
    {
        ADD_CHANGESETS: handle_add_changesets,
        ERROR_APPLY_CHANGESETS: handle_error_apply_changesets,
        CLEAR_CHANGESETS: handle_clear_changesets,
    },
    ChangesetState(error=None, changesets=[]),
)
