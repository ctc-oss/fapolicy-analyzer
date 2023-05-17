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
from importlib import reload
from unittest.mock import MagicMock

import pytest
from callee import InstanceOf
from callee.attributes import Attrs

import fapolicy_analyzer.ui.store as store
from fapolicy_analyzer.redux import Action, ReduxFeatureModule, create_store
from fapolicy_analyzer.ui.actions import (
    start_profiling,
    ERROR_PROFILER_INIT,
    ERROR_PROFILER_EXEC,
    stop_profiling,
)
from fapolicy_analyzer.ui.features import create_profiler_feature
from fapolicy_analyzer.ui.strings import PROFILER_INIT_ERROR, PROFILER_EXEC_ERROR


@pytest.fixture
def mock_dispatch():
    return MagicMock()


@pytest.fixture(autouse=True)
def mock_idle_add(mocker):
    mock_glib = mocker.patch("fapolicy_analyzer.ui.features.profiler_feature.GLib")
    mock_glib.idle_add = lambda fn, *args: fn(*args)
    return mock_glib


@pytest.fixture(autouse=True)
def reload_store():
    reload(store)


def test_creates_profiler_feature(mock_dispatch):
    assert isinstance(create_profiler_feature(mock_dispatch), ReduxFeatureModule)


def test_start_profiler(mock_dispatch, mocker):
    cmd = "foo"
    profiler = MagicMock()
    mock_profiler = mocker.patch(
        "fapolicy_analyzer.ui.features.profiler_feature.Profiler",
        return_value=profiler,
    )
    store = create_store()
    store.add_feature_module(create_profiler_feature(mock_dispatch))
    store.dispatch(start_profiling({"cmd": cmd}))
    mock_profiler.assert_called()


def test_start_profiler_with_init_error(mock_dispatch, mocker):
    mock_profiler = mocker.patch(
        "fapolicy_analyzer.ui.features.profiler_feature.Profiler",
        side_effect=RuntimeError(),
    )
    store = create_store()
    store.add_feature_module(create_profiler_feature(mock_dispatch))
    store.dispatch(start_profiling({"cmd": "foo"}))
    mock_profiler.assert_called()
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ERROR_PROFILER_INIT,
            payload=PROFILER_INIT_ERROR,
        )
    )


def test_start_profiler_with_exec_error(mock_dispatch, mocker):
    profiler = MagicMock()
    profiler.profile.side_effect = RuntimeError()
    mock_profiler_ctor = mocker.patch(
        "fapolicy_analyzer.ui.features.profiler_feature.Profiler",
        return_value=profiler,
    )
    store = create_store()
    store.add_feature_module(create_profiler_feature(mock_dispatch))
    store.dispatch(start_profiling({"cmd": "foo"}))
    mock_profiler_ctor.assert_called()
    profiler.profile.assert_called()
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ERROR_PROFILER_EXEC,
            payload=PROFILER_EXEC_ERROR,
        )
    )


def test_kill_profiler(mock_dispatch, mocker):
    handle = MagicMock()
    profiler = MagicMock()
    profiler.profile.return_value = handle
    mock_profiler_ctor = mocker.patch(
        "fapolicy_analyzer.ui.features.profiler_feature.Profiler",
        return_value=profiler,
    )
    store = create_store()
    store.add_feature_module(create_profiler_feature(mock_dispatch))
    store.dispatch(start_profiling({"cmd": "foo"}))
    mock_profiler_ctor.assert_called()
    profiler.profile.assert_called()
    store.dispatch(stop_profiling())
    handle.kill.assert_called()
