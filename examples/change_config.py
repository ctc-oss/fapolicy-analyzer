# Copyright Concurrent Technologies Corporation 2023
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

from fapolicy_analyzer import *
from fapolicy_analyzer import ConfigChangeset as Changeset


# a system represents the state of the host sytems
s1 = System()
print(s1.config_text())

# changeset deserializes rule text into applicable rules
xs1 = Changeset()

# a changeset has no source prior to parsing
assert xs1.text() is None

txt = """
permissive=1
"""
xs1.parse(txt)
s2 = s1.apply_config_changes(xs1)

print(s2.config_text())

print(config_difference(s1, s2))
