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
print(f"system1 has {len(s1.ancillary_trust())} trust entries")

# changeset represents changes to trust
xs1 = Changeset()
for p in it.islice(pathlib.Path("/bin").iterdir(), 5):
    xs1.add_trust(str(p))
print(f"adding {xs1.len()} trust entries")

# changesets are inexpensive
xs2 = Changeset()
for p in it.islice(pathlib.Path("/bin").iterdir(), 5, 10):
    xs2.add_trust(str(p))
print(f"adding {xs2.len()} trust entries")

# changesets get applied to a system, producing a new system
s2 = s1.apply_changeset(xs1)
print(f"system2 has {len(s2.ancillary_trust())} trust entries")

# the new system can have changes applied to it
s3 = s2.apply_changeset(xs2)
print(f"system3 has {len(s3.ancillary_trust())} trust entries")

# a system is deployed, updating the fapolicyd ancillary trust
# s2.deploy()

# the output is
# ==================================
# system1 has 0 trust entries
# adding 5 trust entries
# adding 5 trust entries
# applying changeset to current state...
# system2 has 5 trust entries
# applying changeset to current state...
# system3 has 10 trust entries
