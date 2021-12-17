# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
#
#
# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
from fapolicy_analyzer import *

# config is loaded from $HOME/.config/fapolicy-analyzer/fapolicy-analyzer.toml
s1 = System()
print(f"found {len(s1.users())} system users")
print(f"found {len(s1.groups())} system groups")

umap = {u.id: u.name for u in s1.users()}
gmap = {g.id: g.name for g in s1.groups()}
for e in s1.events_from("events0.log")[:5]:
    print({"u": umap[e.uid],
           "g": gmap[e.gid],
           "s": {
               "file": e.subject.file,
               "trust": e.subject.trust,
               "access": e.subject.access
           },
           "o": {
               "file": e.object.file,
               "trust": e.object.trust,
               "access": e.object.access,
               "mode": e.object.mode
           }})
print("...")
