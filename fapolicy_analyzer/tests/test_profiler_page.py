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
import datetime

import gi
import pytest
from callee import InstanceOf, Attrs

from fapolicy_analyzer.redux import Action
from fapolicy_analyzer.ui.actions import (
    PROFILING_KILL_REQUEST,
    PROFILER_CLEAR_STATE_CMD,
    START_PROFILING_REQUEST,
    ADD_NOTIFICATION
)
from fapolicy_analyzer.ui.reducers.profiler_reducer import profiler_state, ProfilerState
from fapolicy_analyzer.ui.store import init_store
from mocks import mock_System
from fapolicy_analyzer.ui.profiler_page import ProfilerPage
from fapolicy_analyzer.ui.fapd_manager import FapdManager
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("fapolicy_analyzer.ui.profiler_page.dispatch")


@pytest.fixture
def widget(mocker):
    init_store(mock_System())
    return ProfilerPage(FapdManager(False))


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def get_output_text(widget):
    textBuffer = widget.get_object("profilerOutput").get_buffer()
    return textBuffer.get_text(
        textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
    )


def test_get_entry_dict(widget):
    widget.update_input_fields("foo", "root", "/tmp", None)
    conf = widget.get_entry_dict()
    assert conf.get("cmd") == "foo"
    assert conf.get("uid") == "root"
    assert conf.get("pwd") == "/tmp"
    assert conf.get("env") is None


def test_make_profiling_args(widget):
    widget.update_input_fields("ls", "root", "/tmp", "FOO=BAR,BAZ=BOO")
    profiling_args = widget._make_profiling_args()
    assert profiling_args.get("cmd") == "ls"
    assert profiling_args.get("uid") == "root"
    assert profiling_args.get("pwd") == "/tmp"
    assert profiling_args.get("env") == "FOO=BAR,BAZ=BOO"
    assert profiling_args.get("env_dict") == {"FOO": "BAR", "BAZ": "BOO"}


def test_stop_profiling_click(widget, mock_dispatch):
    widget.on_stop_clicked()
    assert widget.can_stop is False
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(type=PROFILING_KILL_REQUEST, payload=None)
    )


def test_clear_state_click(widget, mock_dispatch):
    widget.update_input_fields("foo", "root", "/tmp", None)
    widget.on_clear_button_clicked()
    assert widget.get_cmd_text() is None
    assert widget.get_arg_text() is None
    assert widget.get_pwd_text() is None
    assert widget.get_env_text() is None
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(type=PROFILER_CLEAR_STATE_CMD, payload=None)
    )


def test_on_tick(widget):
    state = profiler_state(ProfilerState, cmd="foo", pid=999, duration=42)
    t = datetime.timedelta(seconds=state.duration) if state.duration else ""
    expected = f"{state.pid}: Executing {state.cmd} {t}"
    widget.handle_tick(state)
    assert get_output_text(widget) == expected


def test_start_click(widget, mock_dispatch):
    widget.update_input_fields("ls", "root", "/tmp", None)
    profiling_args = widget._make_profiling_args()

    widget.on_start_clicked()
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(type=START_PROFILING_REQUEST, payload=profiling_args)
    )


def test_start_click_with_env(widget, mock_dispatch):
    widget.update_input_fields("ls", "root", "/tmp", "FOO=BAR,BAZ=BOO")
    profiling_args = widget._make_profiling_args()

    widget.on_start_clicked()
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(type=START_PROFILING_REQUEST, payload=profiling_args)
    )


def test_start_click_with_bad_cmd(widget, mock_dispatch):
    widget.update_input_fields("xX_Xx", "root", "/tmp", "FOO=BAR,BAZ=BOO")
    widget.on_start_clicked()
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(type=ADD_NOTIFICATION)
    )


def test_start_click_with_bad_env(widget, mock_dispatch):
    widget.update_input_fields("ls", "root", "/tmp", "FOO")
    widget.on_start_clicked()
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(type=ADD_NOTIFICATION)
    )


def test_start_click_with_bad_uid(widget, mock_dispatch):
    widget.update_input_fields("ls", "foooooo", "/tmp", "FOO")
    widget.on_start_clicked()
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(type=ADD_NOTIFICATION)
    )
