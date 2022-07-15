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

from unittest.mock import MagicMock

import pytest
from callee import InstanceOf
from callee.attributes import Attrs
from fapolicy_analyzer.ui.actions import ERROR_SYSTEM_INITIALIZATION, SYSTEM_INITIALIZED
from fapolicy_analyzer.ui.features.system_feature import (
    SYSTEM_FEATURE,
    create_system_feature,
)
from redux import Action, ReduxFeatureModule, create_store, select_feature
from rx import operators


@pytest.fixture()
def mock_dispatch():
    return MagicMock()


@pytest.fixture(autouse=True)
def mock_system(mocker):
    return mocker.patch("fapolicy_analyzer.ui.features.system_feature.System")


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


@pytest.fixture
def system_feature_module(mock_dispatch):
    store = create_store()
    store.add_feature_module(create_system_feature(mock_dispatch))
    store.as_observable().pipe(operators.map(select_feature(SYSTEM_FEATURE)))


def test_creates_system_feature(mock_dispatch):
    assert isinstance(create_system_feature(mock_dispatch), ReduxFeatureModule)


def test_initializes_system(mock_dispatch, mock_system):
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


def test_uses_provided_system(mock_dispatch, mock_system):
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


def test_epic(mock_dispatch, system_feature_module):
    store = create_store()
    store.add_feature_module(create_system_feature(mock_dispatch))
    store.root_epic()
