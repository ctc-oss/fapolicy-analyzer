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

from fapolicy_analyzer.redux import Action
from fapolicy_analyzer.ui.actions import (
    ADD_CHANGESETS,
    ADD_NOTIFICATION,
    ANCILLARY_TRUST_LOAD_COMPLETE,
    ANCILLARY_TRUST_LOAD_STARTED,
    APPLY_CHANGESETS,
    CLEAR_CHANGESETS,
    DEPLOY_SYSTEM,
    ERROR_ANCILLARY_TRUST,
    ERROR_APP_CONFIG,
    ERROR_APPLY_CHANGESETS,
    ERROR_DEPLOYING_SYSTEM,
    ERROR_EVENTS,
    ERROR_GROUPS,
    ERROR_RULES,
    ERROR_RULES_TEXT,
    ERROR_SYSTEM_INITIALIZATION,
    ERROR_SYSTEM_TRUST,
    ERROR_USERS,
    INIT_SYSTEM,
    MODIFY_RULES_TEXT,
    RECEIVED_ANCILLARY_TRUST_UPDATE,
    RECEIVED_APP_CONFIG,
    RECEIVED_EVENTS,
    RECEIVED_GROUPS,
    RECEIVED_RULES,
    RECEIVED_RULES_TEXT,
    RECEIVED_SYSTEM_TRUST_UPDATE,
    RECEIVED_USERS,
    REMOVE_NOTIFICATION,
    REQUEST_ANCILLARY_TRUST,
    REQUEST_APP_CONFIG,
    REQUEST_EVENTS,
    REQUEST_GROUPS,
    REQUEST_RULES,
    REQUEST_RULES_TEXT,
    REQUEST_SYSTEM_TRUST,
    REQUEST_USERS,
    RESTORE_SYSTEM_CHECKPOINT,
    SET_SYSTEM_CHECKPOINT,
    SYSTEM_CHECKPOINT_SET,
    SYSTEM_DEPLOYED,
    SYSTEM_RECEIVED,
    SYSTEM_TRUST_LOAD_COMPLETE,
    SYSTEM_TRUST_LOAD_STARTED,
    Notification,
    NotificationType,
    add_changesets,
    add_notification,
    ancillary_trust_load_complete,
    ancillary_trust_load_started,
    apply_changesets,
    clear_changesets,
    clear_profiler_state,
    deploy_system,
    error_ancillary_trust,
    error_app_config,
    error_apply_changesets,
    error_deploying_system,
    error_events,
    error_groups,
    error_rules,
    error_rules_text,
    error_system_trust,
    error_users,
    init_system,
    modify_rules_text,
    received_ancillary_trust_update,
    received_app_config,
    received_events,
    received_groups,
    received_rules,
    received_rules_text,
    received_system_trust_update,
    received_users,
    remove_notification,
    request_ancillary_trust,
    request_app_config,
    request_events,
    request_groups,
    request_rules,
    request_rules_text,
    request_system_trust,
    request_users,
    restore_system_checkpoint,
    set_system_checkpoint,
    system_checkpoint_set,
    system_deployed,
    system_initialization_error,
    system_received,
    system_trust_load_complete,
    system_trust_load_started,
    set_profiler_output,
    PROFILER_CLEAR_STATE_CMD,
    profiler_done,
    PROFILER_SET_OUTPUT_CMD,
    stop_profiling,
    terminating_profiler,
    profiler_tick,
    PROFILING_KILL_RESPONSE,
    PROFILING_KILL_REQUEST,
    profiler_exec,
    PROFILING_EXEC_EVENT,
    PROFILING_TICK_EVENT,
    PROFILING_INIT_EVENT,
    profiler_init,
    start_profiling,
    START_PROFILING_REQUEST,
    START_PROFILING_RESPONSE,
    profiling_started,
    PROFILING_DONE_EVENT,
)


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


def test_ancillary_trust_load_started():
    action = ancillary_trust_load_started(1)
    assert type(action) is Action
    assert action.type == ANCILLARY_TRUST_LOAD_STARTED
    assert action.payload == 1


def test_received_ancillary_trust_update():
    trust = [MagicMock()]
    action = received_ancillary_trust_update((trust, 1))
    assert type(action) is Action
    assert action.type == RECEIVED_ANCILLARY_TRUST_UPDATE
    assert action.payload == (trust, 1)


def test_ancillary_trust_load_complete():
    action = ancillary_trust_load_complete()
    assert type(action) is Action
    assert action.type == ANCILLARY_TRUST_LOAD_COMPLETE


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


def test_system_trust_load_started():
    action = system_trust_load_started(1)
    assert type(action) is Action
    assert action.type == SYSTEM_TRUST_LOAD_STARTED
    assert action.payload == 1


def test_received_system_trust_update():
    trust = [MagicMock()]
    action = received_system_trust_update((trust, 1))
    assert type(action) is Action
    assert action.type == RECEIVED_SYSTEM_TRUST_UPDATE
    assert action.payload == (trust, 1)


def test_system_trust_load_complete():
    action = system_trust_load_complete()
    assert type(action) is Action
    assert action.type == SYSTEM_TRUST_LOAD_COMPLETE


def test_error_system_trust():
    action = error_system_trust("foo")
    assert type(action) is Action
    assert action.type == ERROR_SYSTEM_TRUST
    assert action.payload == "foo"


def test_deploy_system():
    action = deploy_system()
    assert type(action) is Action
    assert action.type == DEPLOY_SYSTEM
    assert not action.payload


def test_system_deployed():
    action = system_deployed()
    assert type(action) is Action
    assert action.type == SYSTEM_DEPLOYED
    assert not action.payload


def test_error_deploying_system():
    action = error_deploying_system("foo")
    assert type(action) is Action
    assert action.type == ERROR_DEPLOYING_SYSTEM
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


def test_profiler_init_event():
    action = profiler_init()
    assert type(action) is Action
    assert action.type == PROFILING_INIT_EVENT
    assert action.payload is None


def test_profiler_start_request():
    expected = {"cmd": "foo"}
    action = start_profiling(expected)
    assert type(action) is Action
    assert action.type == START_PROFILING_REQUEST
    assert action.payload is expected


def test_profiler_start_response():
    expected = "cmd"
    action = profiling_started(expected)
    assert type(action) is Action
    assert action.type == START_PROFILING_RESPONSE
    assert action.payload is expected


def test_profiler_exec_event():
    action = profiler_exec(999)
    assert type(action) is Action
    assert action.type == PROFILING_EXEC_EVENT
    assert action.payload == 999


def test_profiler_tick_event():
    action = profiler_tick(999)
    assert type(action) is Action
    assert action.type == PROFILING_TICK_EVENT
    assert action.payload == 999


def test_profiler_kill_request():
    action = stop_profiling()
    assert type(action) is Action
    assert action.type == PROFILING_KILL_REQUEST
    assert action.payload is None


def test_profiler_kill_response():
    action = terminating_profiler()
    assert type(action) is Action
    assert action.type == PROFILING_KILL_RESPONSE
    assert action.payload is None


def test_profiler_done():
    action = profiler_done()
    assert type(action) is Action
    assert action.type == PROFILING_DONE_EVENT
    assert action.payload is None


def test_set_output():
    expected = ("foo", "bar", "baz")
    action = set_profiler_output(expected[0], expected[1], expected[2])
    assert type(action) is Action
    assert action.type == PROFILER_SET_OUTPUT_CMD
    assert action.payload == expected


def test_clear_profiler_state():
    action = clear_profiler_state()
    assert type(action) is Action
    assert action.type == PROFILER_CLEAR_STATE_CMD
    assert action.payload is None


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


def test_request_app_config():
    action = request_app_config()
    assert type(action) is Action
    assert action.type == REQUEST_APP_CONFIG
    assert not action.payload


def test_received_app_config():
    config = {"initial_view": "foo"}
    action = received_app_config(config)
    assert type(action) is Action
    assert action.type == RECEIVED_APP_CONFIG
    assert action.payload == config


def test_error_app_config():
    action = error_app_config("foo")
    assert type(action) is Action
    assert action.type == ERROR_APP_CONFIG
    assert action.payload == "foo"
