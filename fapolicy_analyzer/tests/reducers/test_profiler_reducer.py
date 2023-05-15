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
import context  # noqa: F401 # isort: skip
from unittest.mock import MagicMock

from fapolicy_analyzer.ui.reducers.profiler_reducer import (
    ProfilerState,
    handle_start_profiling_request,
    empty_profiler_state,
    handle_clear_profiler_state,
    derive_profiler_state,
    handle_profiler_exec,
    handle_profiler_tick,
    profiler_state,
)


def test_handle_profiler_exec():
    original = profiler_state(ProfilerState, cmd="foo")
    res = handle_profiler_exec(original, MagicMock(payload=999))
    assert res == derive_profiler_state(ProfilerState, original, cmd="foo", pid=999)


def test_handle_profiler_tick():
    original = profiler_state(ProfilerState, cmd="foo")
    res = handle_profiler_tick(original, MagicMock(payload=999))
    assert res == derive_profiler_state(
        ProfilerState, original, cmd="foo", duration=999
    )


def test_handle_clear_profiler_state():
    original = profiler_state(ProfilerState, cmd="foo", uid="root", pwd="/")
    res = handle_clear_profiler_state(original, MagicMock())
    assert res == derive_profiler_state(
        ProfilerState, original, cmd=None, uid=None, pwd=None
    )


def test_handle_start_profiling_request():
    args = {"cmd": "foo", "uid": "root"}
    res = handle_start_profiling_request(
        empty_profiler_state(), MagicMock(payload=args)
    )
    assert res == profiler_state(ProfilerState, uid="root")

    args = {"cmd": "foo", "pwd": "/"}
    res = handle_start_profiling_request(
        empty_profiler_state(), MagicMock(payload=args)
    )
    assert res == profiler_state(ProfilerState, pwd="/")

    args = {"cmd": "foo", "uid": "root", "pwd": "/"}
    res = handle_start_profiling_request(
        empty_profiler_state(), MagicMock(payload=args)
    )
    assert res == profiler_state(ProfilerState, uid="root", pwd="/")
