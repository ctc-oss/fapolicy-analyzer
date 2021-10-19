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
