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

from typing import Dict

from fapolicy_analyzer.redux import Action, Reducer, handle_actions
from fapolicy_analyzer.ui.actions import CLEAR_PROFILER_STATE, SET_PROFILER_STATE


def handle_set_profiler_state(state: Dict[str, str], action: Action) -> Dict[str, str]:
    return {**action.payload}


def handle_clear_profiler_state(*args) -> Dict[str, str]:
    return {}


profiler_reducer: Reducer = handle_actions(
    {
        SET_PROFILER_STATE: handle_set_profiler_state,
        CLEAR_PROFILER_STATE: handle_clear_profiler_state,
    },
    {},
)
