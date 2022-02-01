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
from util.acl import get_group_details, get_user_details


def test_get_user_details(mocker):
    mocker.patch("util.acl.subprocess.getstatusoutput", return_value=(0, "foo"))
    assert get_user_details(1) == "foo"


def test_get_user_details_handles_error(mocker):
    mocker.patch("util.acl.subprocess.getstatusoutput", return_value=(1, "foo"))
    assert get_user_details(1) == ""


def test_get_user_details_handles_none(mocker):
    assert get_user_details(None) is None


def test_get_group_details(mocker):
    mocker.patch(
        "util.acl.grp.getgrgid", return_value=("foo", "", 99, ["user1", "user2"])
    )
    assert get_group_details(1) == "name=foo gid=99 users=user1,user2"


def test_get_group_details_handles_error(mocker):
    assert get_group_details(-1) == ""


def test_get_group_details_handles_none(mocker):
    assert get_group_details(None) is None
