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
import pathlib

print("= loading system")
# config is loaded from $HOME/.config/fapolicy-analyzer/fapolicy-analyzer.toml
s1 = System()
print(f"system1 has {len(s1.ancillary_trust())} trust entries")

print("= building changeset")
xs = Changeset()
for p in pathlib.Path("/bin").iterdir():
    xs.add_trust(str(p))
print(f"adding {xs.len()} trust entries")

print("= applying changes")
s2 = s1.apply_changeset(xs)
print(f"system2 has {len(s1.ancillary_trust())} trust entries")
for t in s2.ancillary_trust():
    print(f"{t.status} {t.path} {t.size} {t.hash}")

print("= deploying system")
s2.deploy()
