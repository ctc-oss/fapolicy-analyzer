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
from fapolicy_analyzer import Changeset
from redux import Action, Reducer, handle_actions
from typing import Sequence, cast
from fapolicy_analyzer.ui.actions import (
    ADD_CHANGESETS,
    CLEAR_CHANGESETS,
)


def handle_add_changesets(
    state: Sequence[Changeset], action: Action
) -> Sequence[Changeset]:
    payload = cast(Sequence[Changeset], action.payload)
    return (*state, *payload)


def handle_clear_changesets(
    state: Sequence[Changeset], action: Action
) -> Sequence[Changeset]:
    return []


changeset_reducer: Reducer = handle_actions(
    {
        ADD_CHANGESETS: handle_add_changesets,
        CLEAR_CHANGESETS: handle_clear_changesets,
    },
    [],
)
