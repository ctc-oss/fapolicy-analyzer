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
xs1.parse(txt)

# a valid rule without marker
txt = """
allow perm=any all : all
"""
xs1.parse(txt)


# markers are relative to the rules.d dir
# if using fapolicyd.rules markers are not supported

print("# a valid rule with marker")
txt = """
[foo.rules]
allow perm=any all : all
"""
xs1.parse(txt)
for r in xs1.rules():
    print(r)

print("# multiple valid rules with markers")
txt = """
[foo.rules]
allow perm=exec all : all

[bar.rules]
deny perm=any all : all
"""
xs1.parse(txt)
for r in xs1.rules():
    print(r)

print("# valid rules under single marker")
txt = """
[foo.rules]
allow perm=exec all : all
deny perm=any all : all
"""
xs1.parse(txt)
for r in xs1.rules():
    print(r)

print("# empty marker")
txt = """
[foo.rules]
allow perm=exec all : all

[bar.rules]
"""
xs1.parse(txt)
for r in xs1.rules():
    print(r)

print("# malformed marker")
txt = """
[foo.rules
"""
try:
    xs1.parse(txt)
except RuntimeError as e:
    # todo;; we need those custom exceptions... without them we
    #        are reduced to makeshift string based protocols
    (line, msg, src) = str(e).split(":", 2)
    print(f"failed to deserialize: {msg}")
    print(f"\tline {line}: {src}")
