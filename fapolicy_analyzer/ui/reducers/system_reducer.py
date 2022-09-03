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

from typing import Any, NamedTuple, Optional, cast

from fapolicy_analyzer import System
from fapolicy_analyzer.redux import Action, Reducer, combine_reducers, handle_actions
from fapolicy_analyzer.ui.actions import (
    ADD_CHANGESETS,
    CLEAR_CHANGESETS,
    ERROR_DEPLOYING_SYSTEM,
    ERROR_SYSTEM_INITIALIZATION,
    SYSTEM_CHECKPOINT_SET,
    SYSTEM_DEPLOYED,
    SYSTEM_RECEIVED,
)
from fapolicy_analyzer.ui.reducers.ancillary_trust_reducer import (
    ancillary_trust_reducer,
)
from fapolicy_analyzer.ui.reducers.changeset_reducer import changeset_reducer
from fapolicy_analyzer.ui.reducers.event_reducer import event_reducer
from fapolicy_analyzer.ui.reducers.group_reducer import group_reducer
from fapolicy_analyzer.ui.reducers.profiler_reducer import profiler_reducer
from fapolicy_analyzer.ui.reducers.rule_reducer import rule_reducer
from fapolicy_analyzer.ui.reducers.rules_text_reducer import rules_text_reducer
from fapolicy_analyzer.ui.reducers.system_trust_reducer import system_trust_reducer
from fapolicy_analyzer.ui.reducers.user_reducer import user_reducer


class SystemState(NamedTuple):
    error: Optional[str]
    system: System
    checkpoint: System
    deployed: bool


def _create_state(state: SystemState, **kwargs: Optional[Any]) -> SystemState:
    return SystemState(**{**state._asdict(), **kwargs})


def handle_system_received(state: SystemState, action: Action) -> SystemState:
    payload = cast(System, action.payload)
    return _create_state(state, system=payload)


def handle_error_system_initialization(
    state: SystemState, action: Action
) -> SystemState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload)


def handle_system_checkpoint_set(state: SystemState, action: Action) -> SystemState:
    payload = cast(System, action.payload)
    return _create_state(state, checkpoint=payload)


def handle_system_deployed(state: SystemState, action: Action) -> SystemState:
    return _create_state(state, error=None, deployed=True)


def handle_error_deploying_system(state: SystemState, action: Action) -> SystemState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload)


def handle_add_changesets(state: SystemState, action: Action) -> SystemState:
    return _create_state(state, error=None, deployed=False)


def handle_clear_changesets(state: SystemState, action: Action) -> SystemState:
    return _create_state(state, error=None, deployed=True)


system_reducer: Reducer = combine_reducers(
    {
        "system": handle_actions(
            {
                SYSTEM_RECEIVED: handle_system_received,
                ERROR_SYSTEM_INITIALIZATION: handle_error_system_initialization,
                SYSTEM_CHECKPOINT_SET: handle_system_checkpoint_set,
                SYSTEM_DEPLOYED: handle_system_deployed,
                ERROR_DEPLOYING_SYSTEM: handle_error_deploying_system,
                ADD_CHANGESETS: handle_add_changesets,
                CLEAR_CHANGESETS: handle_clear_changesets,
            },
            SystemState(error=None, system=None, checkpoint=None, deployed=False),
        ),
        "ancillary_trust": ancillary_trust_reducer,
        "changesets": changeset_reducer,
        "events": event_reducer,
        "groups": group_reducer,
        "profiler": profiler_reducer,
        "rules": rule_reducer,
        "rules_text": rules_text_reducer,
        "system_trust": system_trust_reducer,
        "users": user_reducer,
    }
)
