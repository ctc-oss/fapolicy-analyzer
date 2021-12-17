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
from typing import cast

from redux import Action, Reducer, create_action, handle_actions

from .action import ACTION_SET_VISIBILITY_FILTER, VisibilityFilters


def handle_visibility_filter(state: VisibilityFilters,
                             action: Action) -> VisibilityFilters:
    payload = cast(VisibilityFilters, action.payload)
    print('payload', payload)
    return payload


visibility_filter: Reducer = handle_actions(
    {ACTION_SET_VISIBILITY_FILTER: handle_visibility_filter}, VisibilityFilters.SHOW_ALL)
