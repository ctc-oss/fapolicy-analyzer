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

from typing import Any, Dict, NamedTuple, Optional, cast

from fapolicy_analyzer.redux import Action, Reducer, handle_actions
from fapolicy_analyzer.ui.actions import (
    ERROR_APP_CONFIG,
    RECEIVED_APP_CONFIG,
    REQUEST_APP_CONFIG,
)
from fapolicy_analyzer.ui.types import PAGE_SELECTION


class AppConfigState(NamedTuple):
    loading: bool
    initial_view: PAGE_SELECTION
    error: Optional[str]


def _create_state(state: AppConfigState, **kwargs: Optional[Any]) -> AppConfigState:
    return AppConfigState(**{**state._asdict(), **kwargs})


def handle_request_app_config(state: AppConfigState, action: Action) -> AppConfigState:
    return _create_state(state, loading=True, error=None)


def handle_received_app_config(state: AppConfigState, action: Action) -> AppConfigState:
    payload = cast(Dict[str, str], action.payload)
    return _create_state(
        state,
        initial_view=payload.get("initial_view", PAGE_SELECTION.RULES_ADMIN),
        error=None,
        loading=False,
    )


def handle_error_app_config(state: AppConfigState, action: Action) -> AppConfigState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload, loading=False)


application_reducer: Reducer = handle_actions(
    {
        REQUEST_APP_CONFIG: handle_request_app_config,
        RECEIVED_APP_CONFIG: handle_received_app_config,
        ERROR_APP_CONFIG: handle_error_app_config,
    },
    AppConfigState(loading=False, initial_view=PAGE_SELECTION.RULES_ADMIN, error=None),
)
