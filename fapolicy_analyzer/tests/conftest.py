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

from unittest.mock import Mock


def assert_not_any_call(self, *args, **kwargs):
    """
    Extends the unittest.Mock object by adding an assert_not_called_with method.
    This asserts the mock has not been called with the specified arguments.
    """
    try:
        self.assert_any_call(*args, **kwargs)
    except AssertionError:
        return
    raise AssertionError(
        "%s call found" % self._format_mock_call_signature(args, kwargs)
    )


Mock.assert_not_any_call = assert_not_any_call
