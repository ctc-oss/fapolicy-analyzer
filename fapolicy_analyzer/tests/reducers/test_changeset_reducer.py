# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
#
#
# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
import context  # noqa: F401
from unittest.mock import MagicMock
from ui.reducers.changeset_reducer import handle_add_changesets, handle_clear_changesets


def test_handle_add_changesets():
    result = handle_add_changesets([], MagicMock(payload=["foo"]))
    assert list(result) == ["foo"]


def test_handle_clear_changesets():
    result = handle_clear_changesets(["foo", "foo2"], MagicMock())
    assert result == []
