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
from redux import Action, Reducer, handle_actions
from typing import Sequence, cast
from fapolicy_analyzer.ui.actions import (
    ADD_NOTIFICATION,
    Notification,
    REMOVE_NOTIFICATION,
)


def handle_add_notification(
    state: Sequence[Notification], action: Action
) -> Sequence[Notification]:
    payload = cast(Notification, action.payload)
    return (*state, payload)


def handle_remove_notification(
    state: Sequence[Notification], action: Action
) -> Sequence[Notification]:
    payload = cast(Notification, action.payload)
    return [n for n in state if n.id != payload.id]


notification_reducer: Reducer = handle_actions(
    {
        ADD_NOTIFICATION: handle_add_notification,
        REMOVE_NOTIFICATION: handle_remove_notification,
    },
    [],
)
