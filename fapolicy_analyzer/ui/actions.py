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

from enum import Enum
from itertools import count
from typing import Any, Dict, Iterator, NamedTuple, Optional, Sequence

from fapolicy_analyzer import Changeset, Event, Group, Rule, System, Trust, User
from fapolicy_analyzer.redux import Action, create_action

INIT_SYSTEM = "INIT_SYSTEM"
SYSTEM_RECEIVED = "SYSTEM_RECEIVED"
ERROR_SYSTEM_INITIALIZATION = "ERROR_SYSTEM_INITIALIZATION"

ADD_NOTIFICATION = "ADD_NOTIFICATION"
REMOVE_NOTIFICATION = "REMOVE_NOTIFICATION"

SET_SYSTEM_CHECKPOINT = "SET_SYSTEM_CHECKPOINT"
SYSTEM_CHECKPOINT_SET = "SYSTEM_CHECKPOINT_SET"
RESTORE_SYSTEM_CHECKPOINT = "RESTORE_SYSTEM_CHECKPOINT"

ADD_CHANGESETS = "ADD_CHANGESETS"
APPLY_CHANGESETS = "APPLY_CHANGESETS"
ERROR_APPLY_CHANGESETS = "ERROR_APPLY_CHANGESETS"
CLEAR_CHANGESETS = "CLEAR_CHANGESET"

REQUEST_ANCILLARY_TRUST = "REQUEST_ANCILLARY_TRUST"
RECEIVED_ANCILLARY_TRUST = "RECEIVED_ANCILLARY_TRUST"
ERROR_ANCILLARY_TRUST = "ERROR_ANCILLARY_TRUST"

REQUEST_SYSTEM_TRUST = "REQUEST_SYSTEM_TRUST"
RECEIVED_SYSTEM_TRUST = "RECEIVED_SYSTEM_TRUST"
ERROR_SYSTEM_TRUST = "ERROR_SYSTEM_TRUST"

DEPLOY_SYSTEM = "DEPLOY_SYSTEM"
SYSTEM_DEPLOYED = "SYSTEM_DEPLOYED"
ERROR_DEPLOYING_SYSTEM = "ERROR_DEPLOYING_SYSTEM"

REQUEST_EVENTS = "REQUEST_EVENTS"
RECEIVED_EVENTS = "RECEIVED_EVENTS"
ERROR_EVENTS = "ERROR_EVENTS"

REQUEST_USERS = "REQUEST_USERS"
RECEIVED_USERS = "RECEIVED_USERS"
ERROR_USERS = "ERROR_USERS"

REQUEST_GROUPS = "REQUEST_GROUPS"
RECEIVED_GROUPS = "RECEIVED_GROUPS"
ERROR_GROUPS = "ERROR_GROUPS"

REQUEST_RULES = "REQUEST_RULES"
RECEIVED_RULES = "RECEIVED_RULES"
ERROR_RULES = "ERROR_RULES"

REQUEST_RULES_TEXT = "REQUEST_RULES_TEXT"
RECEIVED_RULES_TEXT = "RECEIVED_RULES_TEXT"
MODIFY_RULES_TEXT = "MODIFY_RULES_TEXT"
ERROR_RULES_TEXT = "ERROR_RULES_TEXT"

SET_PROFILER_STATE = "SET_PROFILER_STATE"
SET_PROFILER_OUTPUT = "SET_PROFILER_OUTPUT"
SET_PROFILER_ANALYSIS_FILE = "SET_PROFILER_ANALYSIS_FILE"
CLEAR_PROFILER_STATE = "CLEAR_PROFILER_STATE"


def _create_action(type: str, payload: Any = None) -> Action:
    return create_action(type)(payload)


_ids: Iterator[int] = iter(count())


class NotificationType(Enum):
    ERROR = "error"
    WARN = "warn"
    INFO = "info"
    SUCCESS = "success"


class Notification(NamedTuple):
    id: int
    text: str
    type: NotificationType
    category: Optional[str]


def add_notification(
    text: str, type: NotificationType = NotificationType.INFO, category: str = None
) -> Action:
    return _create_action(
        ADD_NOTIFICATION, (Notification(next(_ids), text, type, category))
    )


def remove_notification(id: int) -> Action:
    return _create_action(REMOVE_NOTIFICATION, (Notification(id, "", None, None)))


def add_changesets(*changesets: Changeset) -> Action:
    return _create_action(ADD_CHANGESETS, *changesets)


def apply_changesets(*changesets: Changeset) -> Action:
    return _create_action(APPLY_CHANGESETS, changesets)


def error_apply_changesets(error: str) -> Action:
    return _create_action(ERROR_APPLY_CHANGESETS, error)


def clear_changesets() -> Action:
    return _create_action(CLEAR_CHANGESETS)


def request_ancillary_trust() -> Action:
    return _create_action(REQUEST_ANCILLARY_TRUST)


def received_ancillary_trust(trust: Sequence[Trust]) -> Action:
    return _create_action(RECEIVED_ANCILLARY_TRUST, trust)


def error_ancillary_trust(error: str) -> Action:
    return _create_action(ERROR_ANCILLARY_TRUST, error)


def request_system_trust() -> Action:
    return _create_action(REQUEST_SYSTEM_TRUST)


def received_system_trust(trust: Sequence[Trust]) -> Action:
    return _create_action(RECEIVED_SYSTEM_TRUST, trust)


def error_system_trust(error: str) -> Action:
    return _create_action(ERROR_SYSTEM_TRUST, error)


def deploy_system() -> Action:
    return _create_action(DEPLOY_SYSTEM)


def system_deployed() -> Action:
    return _create_action(SYSTEM_DEPLOYED)


def error_deploying_system(error: str) -> Action:
    return _create_action(ERROR_DEPLOYING_SYSTEM, error)


def set_system_checkpoint() -> Action:
    return _create_action(SET_SYSTEM_CHECKPOINT)


def system_checkpoint_set(checkpoint: System) -> Action:
    return _create_action(SYSTEM_CHECKPOINT_SET, checkpoint)


def restore_system_checkpoint() -> Action:
    return _create_action(RESTORE_SYSTEM_CHECKPOINT)


def request_events(log_type: str, file: str = None) -> Action:
    return _create_action(REQUEST_EVENTS, (log_type, file))


def received_events(events: Sequence[Event]) -> Action:
    return _create_action(RECEIVED_EVENTS, events)


def error_events(error: str) -> Action:
    return _create_action(ERROR_EVENTS, error)


def request_users() -> Action:
    return _create_action(REQUEST_USERS)


def received_users(users: Sequence[User]) -> Action:
    return _create_action(RECEIVED_USERS, users)


def error_users(error: str) -> Action:
    return _create_action(ERROR_USERS, error)


def request_groups() -> Action:
    return _create_action(REQUEST_GROUPS)


def received_groups(groups: Sequence[Group]) -> Action:
    return _create_action(RECEIVED_GROUPS, groups)


def error_groups(error: str) -> Action:
    return _create_action(ERROR_GROUPS, error)


def request_rules() -> Action:
    return _create_action(REQUEST_RULES)


def received_rules(rules: Sequence[Rule]) -> Action:
    return _create_action(RECEIVED_RULES, rules)


def error_rules(error: str) -> Action:
    return _create_action(ERROR_RULES, error)


def request_rules_text() -> Action:
    return _create_action(REQUEST_RULES_TEXT)


def received_rules_text(rules_text: str) -> Action:
    return _create_action(RECEIVED_RULES_TEXT, rules_text)


def modify_rules_text(rules_text: str) -> Action:
    return _create_action(MODIFY_RULES_TEXT, rules_text)


def error_rules_text(error: str) -> Action:
    return _create_action(ERROR_RULES_TEXT, error)


def set_profiler_state(state: Dict[str, str]) -> Action:
    return _create_action(SET_PROFILER_STATE, state)


def set_profiler_output(output: str) -> Action:
    return _create_action(SET_PROFILER_OUTPUT, output)


def set_profiler_analysis_file(file: str) -> Action:
    return _create_action(SET_PROFILER_ANALYSIS_FILE, file)


def clear_profiler_state() -> Action:
    return _create_action(CLEAR_PROFILER_STATE)


def init_system() -> Action:
    return _create_action(INIT_SYSTEM)


def system_received(system: System) -> Action:
    return _create_action(SYSTEM_RECEIVED, system)


def system_initialization_error(error: str) -> Action:
    return _create_action(ERROR_SYSTEM_INITIALIZATION, error)
