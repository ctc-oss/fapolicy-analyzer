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

import grp
import subprocess


def get_user_details(uid):
    if not uid:
        return None
    result = subprocess.getstatusoutput(f"id '{uid}'")
    return result[1] if result[0] == 0 else ""


def get_group_details(gid):
    if not gid:
        return None
    try:
        result = grp.getgrgid(gid)
        return f"name={result[0]} gid={result[2]} users={','.join(result[3])}"
    except KeyError:
        return ""
