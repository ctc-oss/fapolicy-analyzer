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

from fapolicy_analyzer import *
from fapolicy_analyzer import RuleChangeset as Changeset

# config is loaded from $HOME/.config/fapolicy-analyzer/fapolicy-analyzer.toml

# a system represents the state of the host sytems
s1 = System()

# changeset deserializes rule text into applicable rules
xs1 = Changeset()

# an invalid rule
txt = """
foo bar baz
"""
assert not xs1.set(txt)

# a valid rule without marker
txt = """
allow perm=any all : all
"""
assert not xs1.set(txt)

# markers are relative to the rules.d dir
# if using fapolicyd.rules markers are not supported

# a valid rule with marker
txt = """
[foo.rules]
allow perm=any all : all
"""
assert xs1.set(txt)
for r in xs1.get():
    print(r)

print("---")
# multiple valid rules with markers
txt = """
[foo.rules]
allow perm=exec all : all

[bar.rules]
deny perm=any all : all
"""
assert xs1.set(txt)
for r in xs1.get():
    print(r)

print("---")
# valid rules under single marker
txt = """
[foo.rules]
allow perm=exec all : all
deny perm=any all : all
"""
assert xs1.set(txt)
for r in xs1.get():
    print(r)

print("---")
# empty marker
txt = """
[foo.rules]
allow perm=exec all : all

[bar.rules]
"""
assert xs1.set(txt)
for r in xs1.get():
    print(r)

print("---")
# todo;; support parsing relative markers
txt = """
[foo.rules]
allow perm=any all : all
"""
# print(xs1.set(r))
