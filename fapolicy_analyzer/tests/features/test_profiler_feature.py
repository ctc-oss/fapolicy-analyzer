from importlib import reload
from unittest.mock import MagicMock

import pytest
from callee import InstanceOf
from callee.attributes import Attrs

import fapolicy_analyzer.ui.store as store
from fapolicy_analyzer.redux import Action, ReduxFeatureModule, create_store
from fapolicy_analyzer.ui.actions import start_profiling, PROFILER_INIT_ERROR
from fapolicy_analyzer.ui.features import create_profiler_feature


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


def test_start_profiler_with_error(mock_dispatch, mocker):
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
            type=PROFILER_INIT_ERROR,
            payload="Failed to initialize profiler backend",
        )
    )
