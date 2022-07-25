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

from importlib import reload
from unittest.mock import MagicMock

import fapolicy_analyzer.ui.store as store
import pytest
from callee import InstanceOf
from callee.attributes import Attrs
from fapolicy_analyzer.ui.actions import (
    ERROR_SYSTEM_INITIALIZATION,
    SYSTEM_INITIALIZED,
    apply_changesets,
    deploy_ancillary_trust,
    error_ancillary_trust,
    error_events,
    error_groups,
    error_rules,
    error_rules_text,
    error_system_trust,
    error_users,
    received_ancillary_trust,
    received_events,
    received_groups,
    received_rules,
    received_rules_text,
    received_system_trust,
    received_users,
    request_ancillary_trust,
    request_events,
    request_groups,
    request_rules,
    request_rules_text,
    request_system_trust,
    request_users,
)
from fapolicy_analyzer.ui.changeset_wrapper import TrustChangeset
from fapolicy_analyzer.ui.features.system_feature import create_system_feature
from fapolicy_analyzer.ui.store import dispatch, init_store
from fapolicy_analyzer.redux import Action, ReduxFeatureModule, create_store


@pytest.fixture
def mock_dispatch():
    return MagicMock()


@pytest.fixture(autouse=True)
def mock_idle_add(mocker):
    mock_glib = mocker.patch("fapolicy_analyzer.ui.features.system_feature.GLib")
    mock_glib.idle_add = lambda fn, *args: fn(*args)
    return mock_glib


@pytest.fixture(autouse=True)
def mock_threadpoolexecutor(mocker):
    return mocker.patch(
        "fapolicy_analyzer.ui.features.system_feature.ThreadPoolExecutor",
        return_value=MagicMock(submit=lambda x: x()),
    )


@pytest.fixture(autouse=True)
def reload_store():
    reload(store)


def test_creates_system_feature(mock_dispatch):
    assert isinstance(create_system_feature(mock_dispatch), ReduxFeatureModule)


def test_initializes_system(mock_dispatch, mocker):
    mock_system = mocker.patch("fapolicy_analyzer.ui.features.system_feature.System")
    store = create_store()
    store.add_feature_module(create_system_feature(mock_dispatch))
    mock_system.assert_called()
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=SYSTEM_INITIALIZED,
            payload=None,
        )
    )


def test_uses_provided_system(mock_dispatch, mocker):
    mock_system = mocker.patch("fapolicy_analyzer.ui.features.system_feature.System")
    system = mock_system()
    mock_system.reset_mock()
    store = create_store()
    store.add_feature_module(create_system_feature(mock_dispatch, system))
    mock_system.assert_not_called()
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=SYSTEM_INITIALIZED,
            payload=None,
        )
    )


def test_handles_system_initialization_error(mock_dispatch, mocker):
    mock_system = mocker.patch(
        "fapolicy_analyzer.ui.features.system_feature.System",
        side_effect=RuntimeError(),
    )
    store = create_store()
    store.add_feature_module(create_system_feature(mock_dispatch))
    mock_system.assert_called()
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ERROR_SYSTEM_INITIALIZATION,
            payload=None,
        )
    )


def test_apply_changset_epic(mocker):
    mock_add_action = mocker.patch(
        "fapolicy_analyzer.ui.features.system_feature.add_changesets"
    )
    mock_system = MagicMock()
    mock_apply = MagicMock()
    changeset = TrustChangeset()
    changeset.apply_to_system = mock_apply
    init_store(mock_system)
    dispatch(apply_changesets(changeset))
    mock_apply.assert_called_with(mock_system)
    mock_add_action.assert_called_with((changeset,))


def test_apply_changset_epic_error(mocker):
    mock_error_action = mocker.patch(
        "fapolicy_analyzer.ui.features.system_feature.error_apply_changesets"
    )
    mock_changeset = MagicMock(
        apply_to_system=MagicMock(side_effect=Exception("apply changeset error"))
    )
    mock_system = MagicMock()
    init_store(mock_system)
    dispatch(apply_changesets(mock_changeset))
    mock_error_action.assert_called_with("apply changeset error")


@pytest.mark.parametrize(
    "action_to_dispatch, payload, system_fn_to_mock, receive_action_to_mock",
    [
        (request_ancillary_trust, None, "ancillary_trust", received_ancillary_trust),
        (request_events, ("debug", MagicMock()), "load_debuglog", received_events),
        (request_events, ("syslog", None), "load_syslog", received_events),
        (request_users, None, "users", received_users),
        (request_groups, None, "groups", received_groups),
        (request_rules, None, "rules", received_rules),
        (request_rules_text, None, "rules_text", received_rules_text),
        (request_system_trust, None, "system_trust", received_system_trust),
    ],
)
def test_request_epic(
    action_to_dispatch, payload, system_fn_to_mock, receive_action_to_mock, mocker
):
    mock_return_value = MagicMock()
    mock_system_fn = MagicMock(return_value=mock_return_value)
    mock_system = MagicMock(**{system_fn_to_mock: mock_system_fn})
    mock_received_action = mocker.patch(
        f"fapolicy_analyzer.ui.features.system_feature.{receive_action_to_mock.__name__}"
    )

    init_store(mock_system)
    dispatch(action_to_dispatch(*(payload or [])))

    mock_system_fn.assert_called()
    mock_received_action.assert_called_with(mock_return_value)


@pytest.mark.parametrize(
    "action_to_dispatch, payload, system_fn_to_mock, error_action_to_mock",
    [
        (request_ancillary_trust, None, "ancillary_trust", error_ancillary_trust),
        (request_events, ("debug", MagicMock()), "load_debuglog", error_events),
        (request_events, ("syslog", None), "load_syslog", error_events),
        (request_users, None, "users", error_users),
        (request_groups, None, "groups", error_groups),
        (request_rules, None, "rules", error_rules),
        (request_rules_text, None, "rules_text", error_rules_text),
        (request_system_trust, None, "system_trust", error_system_trust),
    ],
)
def test_request_epic_error(
    action_to_dispatch, payload, system_fn_to_mock, error_action_to_mock, mocker
):
    mock_system = MagicMock(
        **{
            system_fn_to_mock: MagicMock(
                side_effect=Exception(f"{system_fn_to_mock} error")
            )
        }
    )
    mock_error_action = mocker.patch(
        f"fapolicy_analyzer.ui.features.system_feature.{error_action_to_mock.__name__}"
    )
    init_store(mock_system)
    dispatch(action_to_dispatch(*(payload or [])))
    mock_error_action.assert_called_with(f"{system_fn_to_mock} error")


def test_request_events_epic_bad_request(mocker):
    mock_received_action = mocker.patch(
        "fapolicy_analyzer.ui.features.system_feature.received_events"
    )

    init_store(MagicMock())
    dispatch(request_events("foo", None))

    mock_received_action.assert_called_with([])


def test_deploy_ancillary_trust_epic(mocker):
    mock_system = MagicMock()
    mock_received_action = mocker.patch(
        "fapolicy_analyzer.ui.features.system_feature.ancillary_trust_deployed"
    )
    init_store(mock_system)
    dispatch(deploy_ancillary_trust())
    mock_system.deploy.assert_called()
    mock_received_action.assert_called_with()


def test_deploy_ancillary_trust_epic_error(mocker):
    mock_system = MagicMock(
        deploy=MagicMock(side_effect=Exception("deploy trust error"))
    )
    mock_error_action = mocker.patch(
        "fapolicy_analyzer.ui.features.system_feature.error_deploying_ancillary_trust"
    )
    init_store(mock_system)
    dispatch(deploy_ancillary_trust())
    mock_error_action.assert_called_with("deploy trust error")


def test_deploy_ancillary_trust_epic_snapshot_error(mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.features.system_feature.fapd_dbase_snapshot",
        return_value=False,
    )
    mock_logger = mocker.patch("fapolicy_analyzer.ui.features.system_feature.logging")
    init_store(MagicMock())
    dispatch(deploy_ancillary_trust())
    mock_logger.warning.assert_called_with(
        "Fapolicyd pre-deploy backup failed, continuing with deployment."
    )
