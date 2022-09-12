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
import argparse


def show_event(e):
    s = e.subject
    o = e.object
    print(f'{e.uid}:{e.gid} {s.file} => {o.file}')


parser = argparse.ArgumentParser()
parser.add_argument("path", type=str, help="Event log to analyzer")
args = parser.parse_args()


s = System()
log = s.load_debuglog(args.path)

print(f"Subjects in log: {len(log.subjects())}\n")

print('# Subject events')
for e in log.by_subject('/bin/bash'):
    show_event(e)
print()

for u in s.users():
    ulog = log.by_user(u.id)
    if ulog:
        print(f"# User events - {u.id}")
        for e in ulog:
            show_event(e)
        print()

for g in s.groups():
    glog = log.by_group(g.id)
    if glog:
        print(f"# Group events - {g.id}")
        for e in glog:
            show_event(e)
        print()
