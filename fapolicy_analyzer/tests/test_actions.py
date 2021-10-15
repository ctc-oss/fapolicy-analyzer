import context  # noqa: F401
import pytest
from redux import Action
from ui.actions import (
    ADD_CHANGESETS,
    ADD_NOTIFICATION,
    ANCILLARY_TRUST_DEPLOYED,
    APPLY_CHANGESETS,
    CLEAR_CHANGESETS,
    DEPLOY_ANCILLARY_TRUST,
    ERROR_ANCILLARY_TRUST,
    ERROR_DEPLOYING_ANCILLARY_TRUST,
    ERROR_EVENTS,
    ERROR_GROUPS,
    ERROR_SYSTEM_TRUST,
    ERROR_USERS,
    INIT_SYSTEM,
    RECEIVED_ANCILLARY_TRUST,
    RECEIVED_EVENTS,
    RECEIVED_GROUPS,
    RECEIVED_SYSTEM_TRUST,
    RECEIVED_USERS,
    REMOVE_NOTIFICATION,
    REQUEST_ANCILLARY_TRUST,
    REQUEST_EVENTS,
    REQUEST_GROUPS,
    REQUEST_SYSTEM_TRUST,
    REQUEST_USERS,
    RESTORE_SYSTEM_CHECKPOINT,
    SET_SYSTEM_CHECKPOINT,
    SYSTEM_INITIALIZED,
    Notification,
    NotificationType,
    add_changesets,
    add_notification,
    ancillary_trust_deployed,
    apply_changesets,
    clear_changesets,
    deploy_ancillary_trust,
    error_ancillary_trust,
    error_deploying_ancillary_trust,
    error_events,
    error_groups,
    error_system_trust,
    error_users,
    init_system,
    received_ancillary_trust,
    received_events,
    received_groups,
    received_system_trust,
    received_users,
    remove_notification,
    request_ancillary_trust,
    request_events,
    request_groups,
    request_system_trust,
    request_users,
    restore_system_checkpoint,
    set_system_checkpoint,
    system_initialized,
)
from unittest.mock import MagicMock, Mock


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


def test_request_events():
    action = request_events("fooFile")
    assert type(action) is Action
    assert action.type == REQUEST_EVENTS
    assert action.payload == "fooFile"


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
