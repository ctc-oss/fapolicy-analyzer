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
from fapolicy_analyzer import RuleChangeset as Changeset

# config is loaded from $HOME/.config/fapolicy-analyzer/fapolicy-analyzer.toml

# a system represents the state of the host sytems
s1 = System()
#print(f"system1 has {len(s1.ancillary_trust())} trust entries")


# Important points
# ================
# 1. This is not intended to be a validation API entrypoint
# 2. Validation here is done to prevent invalid deployment,
#    not to provde feedback to the client of the API
# 3. The rules changeset is exported as RuleChangeset for now,
#    but may be later relocated to rules.Changeset
# 4. Relative paths in markers will be supported

# Questions
# ===========
# 1. Should we support finer control of rule ops
#    eg. Add, Rem of individual rules, like trust ops
# 2.


# changeset deserializes rule text into applicable rules
xs1 = Changeset()

# an invalid rule
txt = """
foo bar baz
"""
print(xs1.set(txt))
# False

# a valid rule without marker
txt = """
allow perm=any all : all
"""
print(xs1.set(txt))
# False

# a valid rule with marker
txt = """
[/etc/fapolicyd/rules.d/foo.rules]
allow perm=any all : all
"""
print(xs1.set(txt))
# True

# multiple valid rules with markers
txt = """
[/etc/fapolicyd/rules.d/foo.rules]
allow perm=exec all : all

[/etc/fapolicyd/rules.d/bar.rules]
deny perm=any all : all
"""
print(xs1.set(txt))
# True

# valid rules under single marker
txt = """
[/etc/fapolicyd/rules.d/foo.rules]
allow perm=exec all : all
deny perm=any all : all
"""
print(xs1.set(txt))
# True

# empty marker
txt = """
[/etc/fapolicyd/rules.d/foo.rules]
allow perm=exec all : all

[/etc/fapolicyd/rules.d/bar.rules]
"""
print(xs1.set(txt))
# True


# todo;; support parsing relative markers
txt = """
[foo.rules]
allow perm=any all : all
"""
# print(xs1.set(r))
