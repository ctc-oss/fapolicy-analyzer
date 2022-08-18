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
print("loading system")
s1 = System()
print(f"system1 has {len(s1.rules())} rules defined")

print("building changeset")
xs = Changeset()

# demonstrates: rules / sets / multiple markers
rule_text = """
[05-foo.rules]
%foo=bar,baz
allow perm=exec all : all

[10-bar.rules]
%bing=bam,boom
deny perm=any all : all
"""
assert xs.set(rule_text)

print("applying changes")
s2 = s1.apply_rule_changes(xs)

print(f"system2 has {len(s2.rules())} rules defined")

print("deploying system")
s2.deploy_only()

# display a diff of the rules

assert xs.set(rule_text.replace("bar", "fizz"))

print("diffing additional changes\n")
s3 = s2.apply_rule_changes(xs)
for ln in rules_difference(s2, s3).split("\n"):
    if ln.startswith("+"):
        print('\033[92m', end='')
    elif ln.startswith("-"):
        print('\033[91m', end='')

    print(f"{ln}  \033[0m")
