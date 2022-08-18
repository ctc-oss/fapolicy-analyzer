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

import gi
import pytest
from fapolicy_analyzer.ui.splash_screen import SplashScreen
from fapolicy_analyzer.ui.store import init_store
from rx.subject import Subject

from mocks import mock_System

gi.require_version("GtkSource", "3.0")
from gi.repository import Gtk  # isort: skip


@pytest.fixture
def mock_init_store():
    init_store(mock_System())


@pytest.fixture
def mock_system_features(mocker):
    system_features_mock = Subject()
    mocker.patch(
        "fapolicy_analyzer.ui.splash_screen.get_system_feature",
        return_value=system_features_mock,
    )
    system_features_mock.on_next({"system": MagicMock()})
    return system_features_mock


@pytest.fixture
def widget(mock_init_store, mock_system_features):
    return SplashScreen()


def test_displays_window(widget):
    window = widget.get_ref()
    assert type(window) is Gtk.Window
    contents = window.get_child()
    assert type(contents) is Gtk.Box
    assert Gtk.ProgressBar in [type(c) for c in contents.get_children()]


@pytest.mark.usefixtures("widget")
def test_opens_main_window(mock_system_features, mocker):
    mock_main_window = mocker.patch("fapolicy_analyzer.ui.splash_screen.MainWindow")
    mock_system_features.on_next({"system": MagicMock(system=MagicMock(), error=False)})
    mock_main_window.assert_called_once()


@pytest.mark.usefixtures("widget")
def test_displays_error_dialog(mock_system_features, mocker):
    mock_error_dialog = mocker.patch(
        "fapolicy_analyzer.ui.splash_screen.trust_db_access_failure_dlg"
    )
    mock_exit = mocker.patch("fapolicy_analyzer.ui.splash_screen.sys.exit")
    mock_system_features.on_next({"system": MagicMock(system=None, error=True)})
    mock_error_dialog.assert_called_once()
    mock_exit.assert_called_once()


@pytest.mark.usefixtures("mock_system_features")
def test_updates_progressBar(mocker):
    def mock_get_object(self, name):
        if name == "progressBar":
            return mockProgressBar
        return original_get_object(self, name)

    mockProgressBar = MagicMock(pulse=MagicMock())
    original_get_object = SplashScreen.get_object
    mocker.patch(
        "fapolicy_analyzer.ui.splash_screen.SplashScreen.get_object",
        new=mock_get_object,
    )

    widget = SplashScreen()
    mockProgressBar.pulse.assert_called_once()
    # Not sure how to sleep here without blocking the thread, so just calling the callback directly
    widget.on_timeout()
    assert mockProgressBar.pulse.call_count == 2
