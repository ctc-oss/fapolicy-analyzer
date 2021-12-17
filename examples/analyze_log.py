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


def show_event(e):
    s = e.subject
    o = e.object
    print(f'{e.uid}:{e.gid} {s.file} => {o.file}')


s = System()
log = s.events('tests/data/events1.log')

print(f"Subjects in log: {len(log.subjects())}\n")

print('# Subject events')
for e in log.by_subject('/bin/bash'):
    show_event(e)
print()

print('# User events - 1')
for e in log.by_user(1):
    show_event(e)
print()

print('Group events- 555')
for e in log.by_group(555):
    show_event(e)
print()

print('Group events - 888')
for e in log.by_group(888):
    show_event(e)
