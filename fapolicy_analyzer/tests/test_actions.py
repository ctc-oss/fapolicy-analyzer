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
from redux import Action
from ui.actions import (
    ADD_CHANGESETS,
    ADD_NOTIFICATION,
    ANCILLARY_TRUST_DEPLOYED,
    APPLY_CHANGESETS,
    CLEAR_CHANGESETS,
    DAEMON_INITIALIZED,
    DEPLOY_ANCILLARY_TRUST,
    ERROR_ANCILLARY_TRUST,
    ERROR_DAEMON_START,
    ERROR_DAEMON_STATUS_UPDATE,
    ERROR_DAEMON_STOP,
    ERROR_DEPLOYING_ANCILLARY_TRUST,
    ERROR_EVENTS,
    ERROR_GROUPS,
    ERROR_SYSTEM_TRUST,
    ERROR_USERS,
    INIT_DAEMON,
    INIT_SYSTEM,
    RECEIVED_ANCILLARY_TRUST,
    RECEIVED_DAEMON_START,
    RECEIVED_DAEMON_STATUS_UPDATE,
    RECEIVED_DAEMON_STOP,
    RECEIVED_EVENTS,
    RECEIVED_GROUPS,
    RECEIVED_SYSTEM_TRUST,
    RECEIVED_USERS,
    REMOVE_NOTIFICATION,
    REQUEST_ANCILLARY_TRUST,
    REQUEST_DAEMON_START,
    REQUEST_DAEMON_STOP,
    REQUEST_EVENTS,
    REQUEST_GROUPS,
    REQUEST_SYSTEM_TRUST,
    REQUEST_USERS,
    RESTORE_SYSTEM_CHECKPOINT,
    SET_SYSTEM_CHECKPOINT,
    SYSTEM_INITIALIZED,
    Notification,
    NotificationType,
    DaemonState,
    ServiceStatus,
    add_changesets,
    add_notification,
    ancillary_trust_deployed,
    apply_changesets,
    clear_changesets,
    daemon_initialized,
    deploy_ancillary_trust,
    error_ancillary_trust,
    error_daemon_start,
    error_daemon_status_update,
    error_daemon_stop,
    error_deploying_ancillary_trust,
    error_events,
    error_groups,
    error_system_trust,
    error_users,
    init_daemon,
    init_system,
    received_ancillary_trust,
    received_daemon_start,
    received_daemon_status_update,
    received_daemon_stop,
    received_events,
    received_groups,
    received_system_trust,
    received_users,
    remove_notification,
    request_ancillary_trust,
    request_daemon_start,
    request_daemon_stop,
    request_events,
    request_groups,
    request_system_trust,
    request_users,
    restore_system_checkpoint,
    set_system_checkpoint,
    system_initialized,
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
    assert action.type == SET_SYSTEM_CHECKPOINT
    assert not action.payload


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


def test_init_system():
    action = init_system()
    assert type(action) is Action
    assert action.type == INIT_SYSTEM
    assert not action.payload


def test_system_initialized():
    action = system_initialized()
    assert type(action) is Action
    assert action.type == SYSTEM_INITIALIZED
    assert not action.payload


def test_init_daemon():
    action = init_daemon()
    assert type(action) is Action
    assert action.type == INIT_DAEMON
    assert not action.payload


def test_daemon_initialized():
    action = daemon_initialized()
    assert type(action) is Action
    assert action.type == DAEMON_INITIALIZED
    assert not action.payload


def test_received_daemon_status_update():
    action = received_daemon_status_update(DaemonState(error=None,
                                                       status=ServiceStatus.TRUE))
    assert type(action) is Action
    assert action.type == RECEIVED_DAEMON_STATUS_UPDATE
    assert action.payload
    print(action.payload)


def test_error_daemon_status_update():
    action = error_daemon_status_update("We are handling an error!")
    assert type(action) is Action
    assert action.type == ERROR_DAEMON_STATUS_UPDATE
    assert action.payload
    print(action.payload)


def test_request_daemon_stop():
    action = request_daemon_stop()
    assert type(action) is Action
    assert action.type == REQUEST_DAEMON_STOP
    assert not action.payload


def test_received_daemon_stop():
    action = received_daemon_stop()
    assert type(action) is Action
    assert action.type == RECEIVED_DAEMON_STOP
    assert not action.payload


def test_error_daemon_stop():
    action = error_daemon_stop("We are handling an error!")
    assert type(action) is Action
    assert action.type == ERROR_DAEMON_STOP
    assert action.payload
    print(action.payload)


def test_request_daemon_start():
    action = request_daemon_start()
    assert type(action) is Action
    assert action.type == REQUEST_DAEMON_START
    assert not action.payload


def test_received_daemon_start():
    action = received_daemon_start()
    assert type(action) is Action
    assert action.type == RECEIVED_DAEMON_START
    assert not action.payload


def test_error_daemon_start():
    action = error_daemon_start("We are handling an error!")
    assert type(action) is Action
    assert action.type == ERROR_DAEMON_START
    assert action.payload
    print(action.payload)
