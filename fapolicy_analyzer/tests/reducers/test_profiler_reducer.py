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
    handle_clear_profiler_state,
)


# def test_handle_set_profiler_state():
#     new_state = {"key1": "value1"}
#     result = handle_set_profiler_state(
#         ProfilerState(entry={"oldkey": "oldvalue"}, output="", file=""),
#         MagicMock(payload=new_state)
#     )
#     assert result == ProfilerState(entry=new_state, output="", file="")
#
#
# def test_handle_clear_profiler_state():
#     result = handle_clear_profiler_state(ProfilerState(entry={"oldkey": "oldvalue"}, output="", file=""))
#     assert result == ProfilerState(entry=default_entry, output="", file="")
