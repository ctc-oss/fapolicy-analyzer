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

import gi
import pytest
from fapolicy_analyzer.ui.store import init_store
from mocks import mock_System
from fapolicy_analyzer.ui.profiler_page import ProfilerPage
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("ui.profiler_page.dispatch")


@pytest.fixture
def widget(mock_dispatch, mocker):
    init_store(mock_System())
    return ProfilerPage()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_run_analyzer(widget):
    widget.get_object("dirEntry").set_text("/tmp")
    widget.on_test_activate()
