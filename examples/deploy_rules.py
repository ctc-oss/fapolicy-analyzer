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
assert xs.set(
    """
[05-foo.rules]
%foo=bar,baz
allow perm=exec all : all

[10-bar.rules]
%bing=bam,boom
deny perm=any all : all
"""
)

print("applying changes")
s2 = s1.apply_rule_changes(xs)

print(f"system2 has {len(s2.rules())} rules defined")

print("deploying system")
s2.deploy_only()
