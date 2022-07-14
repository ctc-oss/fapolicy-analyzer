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

from unittest.mock import MagicMock

import context  # noqa: F401


@pytest.fixture()
def initial_state():
    return ChangesetState(changesets=[], error=None)


def test_handle_add_changesets(initial_state):
    result = handle_add_changesets(initial_state, MagicMock(payload=["foo"]))
    assert result == ChangesetState(changesets=["foo"], error=None)


def test_handle_clear_changesets():
    result = handle_clear_changesets(
        ChangesetState(changesets=["foo", "foo2"], error=None), MagicMock()
    )
    assert result == ChangesetState(changesets=[], error=None)


def test_handle_error_apply_changesets(initial_state):
    result = handle_error_apply_changesets(initial_state, MagicMock(payload="foo"))
    assert result == ChangesetState(error="foo", changesets=[])
