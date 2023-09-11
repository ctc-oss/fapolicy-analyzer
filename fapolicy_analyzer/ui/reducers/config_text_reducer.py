# Copyright Concurrent Technologies Corporation 2023
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
    ERROR_CONFIG_TEXT,
    MODIFY_CONFIG_TEXT,
    RECEIVED_CONFIG_TEXT,
    REQUEST_CONFIG_TEXT,
)
from fapolicy_analyzer.redux import Action, Reducer, handle_actions


class ConfigTextState(NamedTuple):
    error: Optional[str]
    loading: bool
    config_text: str
    modified_config_text: str


def _create_state(state: ConfigTextState, **kwargs: Optional[Any]) -> ConfigTextState:
    return ConfigTextState(**{**state._asdict(), **kwargs})


def handle_request_config_text(state: ConfigTextState, _: Action) -> ConfigTextState:
    return _create_state(state, loading=True, error=None)


def handle_received_config_text(state: ConfigTextState, action: Action) -> ConfigTextState:
    payload = cast(str, action.payload)
    return _create_state(state, config_text=payload, error=None, loading=False)


def handle_modify_config_text(state: ConfigTextState, action: Action) -> ConfigTextState:
    payload = cast(str, action.payload)
    return _create_state(state, modified_config_text=payload, error=None, loading=False)


def handle_error_config_text(state: ConfigTextState, action: Action) -> ConfigTextState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload, loading=False)


config_text_reducer: Reducer = handle_actions(
    {
        REQUEST_CONFIG_TEXT: handle_request_config_text,
        RECEIVED_CONFIG_TEXT: handle_received_config_text,
        MODIFY_CONFIG_TEXT: handle_modify_config_text,
        ERROR_CONFIG_TEXT: handle_error_config_text,
    },
    ConfigTextState(error=None, config_text="", loading=False, modified_config_text=""),
)
