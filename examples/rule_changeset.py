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

import pathlib
import itertools as it
from fapolicy_analyzer import *

# config is loaded from $HOME/.config/fapolicy-analyzer/fapolicy-analyzer.toml

# a system represents the state of the host sytems
s1 = System()
#print(f"system1 has {len(s1.ancillary_trust())} trust entries")

# changeset deserializes rule text into applicable rules
xs1 = RuleChangeset()

r = """
foo bar baz
"""
print(xs1.set("foo bar"))

r = """
allow perm=any all : all
"""
print(xs1.set(r))


r = """
[/etc/fapolicyd/rules.d/foo.rules]
allow perm=any all : all
"""
print(xs1.set(r))

# todo;; support parsing abbreviated markers
r = """
[foo.rules]
allow perm=any all : all
"""
# print(xs1.set(r))
