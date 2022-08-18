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

import context  # noqa: F401 # isort: skip
from unittest.mock import MagicMock

import pytest
from fapolicy_analyzer.ui.actions import (
    ADD_CHANGESETS,
    ADD_NOTIFICATION,
    ANCILLARY_TRUST_DEPLOYED,
    APPLY_CHANGESETS,
    CLEAR_CHANGESETS,
    DEPLOY_ANCILLARY_TRUST,
    ERROR_ANCILLARY_TRUST,
    ERROR_APPLY_CHANGESETS,
    ERROR_DEPLOYING_ANCILLARY_TRUST,
    ERROR_EVENTS,
    ERROR_GROUPS,
    ERROR_RULES,
    ERROR_RULES_TEXT,
    ERROR_SYSTEM_INITIALIZATION,
    ERROR_SYSTEM_TRUST,
    ERROR_USERS,
    INIT_SYSTEM,
    MODIFY_RULES_TEXT,
    RECEIVED_ANCILLARY_TRUST,
    RECEIVED_EVENTS,
    RECEIVED_GROUPS,
    RECEIVED_RULES,
    RECEIVED_RULES_TEXT,
    RECEIVED_SYSTEM_TRUST,
    RECEIVED_USERS,
    REMOVE_NOTIFICATION,
    REQUEST_ANCILLARY_TRUST,
    REQUEST_EVENTS,
    REQUEST_GROUPS,
    REQUEST_RULES,
    REQUEST_RULES_TEXT,
    REQUEST_SYSTEM_TRUST,
    REQUEST_USERS,
    RESTORE_SYSTEM_CHECKPOINT,
    SET_SYSTEM_CHECKPOINT,
    SYSTEM_CHECKPOINT_SET,
    SYSTEM_RECEIVED,
    Notification,
    NotificationType,
    add_changesets,
    add_notification,
    ancillary_trust_deployed,
    apply_changesets,
    clear_changesets,
    deploy_ancillary_trust,
    error_ancillary_trust,
    error_apply_changesets,
    error_deploying_ancillary_trust,
    error_events,
    error_groups,
    error_rules,
    error_rules_text,
    error_system_trust,
    error_users,
    init_system,
    modify_rules_text,
    received_ancillary_trust,
    received_events,
    received_groups,
    received_rules,
    received_rules_text,
    received_system_trust,
    received_users,
    remove_notification,
    request_ancillary_trust,
    request_events,
    request_groups,
    request_rules,
    request_rules_text,
    request_system_trust,
    request_users,
    restore_system_checkpoint,
    set_system_checkpoint,
    system_checkpoint_set,
    system_initialization_error,
    system_received,
)
from fapolicy_analyzer.redux import Action


@pytest.mark.parametrize("notification_type", [t for t in list(NotificationType)])
def test_add_notification(notification_type):
    action = add_notification("foo", notification_type)
    assert type(action) is Action
    assert action.type == ADD_NOTIFICATION
    assert type(action.payload) is Notification
    assert action.payload.id >= 0
    assert action.payload.text == "foo"
    assert action.payload.type is notification_type


def test_remove_notification():
    action = remove_notification(100)
    assert type(action) is Action
    assert action.type == REMOVE_NOTIFICATION
    assert type(action.payload) is Notification
    assert action.payload.id == 100
    assert action.payload.text == ""
    assert action.payload.type is None


def test_add_changesets():
    changeset = MagicMock()
    action = add_changesets(changeset)
    assert type(action) is Action
    assert action.type == ADD_CHANGESETS
    assert action.payload == changeset


def test_apply_changesets():
    changeset = MagicMock()
    action = apply_changesets(changeset)
    assert type(action) is Action
    assert action.type == APPLY_CHANGESETS
    assert action.payload == (changeset,)


def test_error_apply_changesets():
    action = error_apply_changesets("foo")
    assert type(action) is Action
    assert action.type == ERROR_APPLY_CHANGESETS
    assert action.payload == "foo"


def test_clear_changesets():
    action = clear_changesets()
    assert type(action) is Action
    assert action.type == CLEAR_CHANGESETS
    assert not action.payload


def test_request_ancillary_trust():
    action = request_ancillary_trust()
    assert type(action) is Action
    assert action.type == REQUEST_ANCILLARY_TRUST
    assert not action.payload


def test_received_ancillary_trust():
    trust = [MagicMock()]
    action = received_ancillary_trust(trust)
    assert type(action) is Action
    assert action.type == RECEIVED_ANCILLARY_TRUST
    assert action.payload == trust


def test_error_ancillary_trust():
    action = error_ancillary_trust("foo")
    assert type(action) is Action
    assert action.type == ERROR_ANCILLARY_TRUST
    assert action.payload == "foo"


def test_request_system_trust():
    action = request_system_trust()
    assert type(action) is Action
    assert action.type == REQUEST_SYSTEM_TRUST
    assert not action.payload


def test_received_system_trust():
    trust = [MagicMock()]
    action = received_system_trust(trust)
    assert type(action) is Action
    assert action.type == RECEIVED_SYSTEM_TRUST
    assert action.payload == trust


def test_error_system_trust():
    action = error_system_trust("foo")
    assert type(action) is Action
    assert action.type == ERROR_SYSTEM_TRUST
    assert action.payload == "foo"


def test_deploy_ancillary_trust():
    action = deploy_ancillary_trust()
    assert type(action) is Action
    assert action.type == DEPLOY_ANCILLARY_TRUST
    assert not action.payload


def test_ancillary_trust_deployed():
    action = ancillary_trust_deployed()
    assert type(action) is Action
    assert action.type == ANCILLARY_TRUST_DEPLOYED
    assert not action.payload


def test_error_deploying_ancillary_trust():
    action = error_deploying_ancillary_trust("foo")
    assert type(action) is Action
    assert action.type == ERROR_DEPLOYING_ANCILLARY_TRUST
    assert action.payload == "foo"


def test_set_system_checkpoint():
    action = set_system_checkpoint()
    assert type(action) is Action
    assert action.type == SET_SYSTEM_CHECKPOINT
    assert not action.payload


def test_system_checkpoint_set():
    mock_checkpoint = MagicMock()
    action = system_checkpoint_set(mock_checkpoint)
    assert type(action) is Action
    assert action.type == SYSTEM_CHECKPOINT_SET
    assert action.payload == mock_checkpoint


def test_restore_system_checkpoint():
    action = restore_system_checkpoint()
    assert action.type == RESTORE_SYSTEM_CHECKPOINT
    assert not action.payload


def test_request_sys_log_events():
    action = request_events("syslog")
    assert type(action) is Action
    assert action.type == REQUEST_EVENTS
    assert action.payload == ("syslog", None)


def test_request_debug_log_events():
    action = request_events("debug", "foo")
    assert type(action) is Action
    assert action.type == REQUEST_EVENTS
    assert action.payload == ("debug", "foo")


def test_received_events():
    events = [MagicMock()]
    action = received_events(events)
    assert type(action) is Action
    assert action.type == RECEIVED_EVENTS
    assert action.payload == events


def test_error_events():
    action = error_events("foo")
    assert type(action) is Action
    assert action.type == ERROR_EVENTS
    assert action.payload == "foo"


def test_request_users():
    action = request_users()
    assert type(action) is Action
    assert action.type == REQUEST_USERS
    assert not action.payload


def test_received_users():
    users = [MagicMock()]
    action = received_users(users)
    assert type(action) is Action
    assert action.type == RECEIVED_USERS
    assert action.payload == users


def test_error_users():
    action = error_users("foo")
    assert type(action) is Action
    assert action.type == ERROR_USERS
    assert action.payload == "foo"


def test_request_groups():
    action = request_groups()
    assert type(action) is Action
    assert action.type == REQUEST_GROUPS
    assert not action.payload


def test_received_groups():
    groups = [MagicMock()]
    action = received_groups(groups)
    assert type(action) is Action
    assert action.type == RECEIVED_GROUPS
    assert action.payload == groups


def test_error_groups():
    action = error_groups("foo")
    assert type(action) is Action
    assert action.type == ERROR_GROUPS
    assert action.payload == "foo"


def test_request_rules():
    action = request_rules()
    assert type(action) is Action
    assert action.type == REQUEST_RULES
    assert not action.payload


def test_received_rules():
    rules = [MagicMock()]
    action = received_rules(rules)
    assert type(action) is Action
    assert action.type == RECEIVED_RULES
    assert action.payload == rules


def test_error_rules():
    action = error_rules("foo")
    assert type(action) is Action
    assert action.type == ERROR_RULES
    assert action.payload == "foo"


def test_request_rules_text():
    action = request_rules_text()
    assert type(action) is Action
    assert action.type == REQUEST_RULES_TEXT
    assert not action.payload


def test_received_rules_text():
    text = "some awesome rules!"
    action = received_rules_text(text)
    assert type(action) is Action
    assert action.type == RECEIVED_RULES_TEXT
    assert action.payload == text


def test_modify_rules_text():
    text = "some modified rules!"
    action = modify_rules_text(text)
    assert type(action) is Action
    assert action.type == MODIFY_RULES_TEXT
    assert action.payload == text


def test_error_rules_text():
    action = error_rules_text("foo")
    assert type(action) is Action
    assert action.type == ERROR_RULES_TEXT
    assert action.payload == "foo"


def test_init_system():
    action = init_system()
    assert type(action) is Action
    assert action.type == INIT_SYSTEM
    assert not action.payload


def test_system_received():
    mock_system = MagicMock()
    action = system_received(mock_system)
    assert type(action) is Action
    assert action.type == SYSTEM_RECEIVED
    assert action.payload == mock_system


def test_system_initialization_error():
    action = system_initialization_error("foo")
    assert type(action) is Action
    assert action.type == ERROR_SYSTEM_INITIALIZATION
    assert action.payload == "foo"
