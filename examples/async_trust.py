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

import threading
import time
import argparse

from rx import operators

from fapolicy_analyzer import *
from fapolicy_analyzer.redux import (
  create_store, select_feature
)
from fapolicy_analyzer.ui.actions import system_received
from fapolicy_analyzer.ui.features import SYSTEM_FEATURE, create_system_feature


parser = argparse.ArgumentParser()
parser.add_argument("trust_type", default="all", choices=["all", "system", "file"], nargs='?', help="trust type to show")
args = parser.parse_args()

print(f"checking {args.trust_type} trust")

store = create_store()

t = time.time()

# to avoid breaking master there is an alternative
# unchecked function to create a System. after the ui
# integrates the callbacks this function will go away
# and the main System ctor will load unchecked trust
# s1 = System()
s1 = unchecked_system()

duration = time.time() - t
print(f"system created in {duration} seconds")

# check to ensure that merging trust does not change the original size of the trust db
if args.trust_type == "file":
    check_fn = check_ancillary_trust
    original_trust_size = len(s1.ancillary_trust())
elif args.trust_type == "system":
    check_fn = check_system_trust
    original_trust_size = len(s1.system_trust())
else:
    check_fn = check_all_trust
    original_trust_size = len(s1.ancillary_trust()) + len(s1.system_trust())


print(f"system contains {original_trust_size} unchecked system trust entries")

store.add_feature_module(create_system_feature(store.dispatch, s1))
done = threading.Event()


# this is very slow...
def checked_entries(system):
    return list(filter(lambda trust: trust.actual, system.system_trust()))


def next_system(system_state):
    system = system_state.get('system').system
    # assert len(system.system_trust()) == len(s1.system_trust())
    # assert len(system.system_trust()) == original_trust_size


def system_error(e):
    print(f"error: {e}")


def available(updates, count):
    # merge the updated trust into the system
    s1.merge(updates)
    # dispatch the system to the redux store
    store.dispatch(system_received(s1))
    print(f"progress {int(count / original_trust_size * 100)}%", end='\r')
    # print(f"{pct:4}% {len(checked_entries(s1))}")


def completed():
    print(f"\ndone!")
    done.set()


f = store.as_observable().pipe(operators.map(select_feature(SYSTEM_FEATURE)))
f.subscribe(
    on_next=next_system,
    on_error=system_error,
    on_completed=None,
)

t = time.time()

# using the check_disk_trust binding we can set callbacks for when
# 1. new data is available
# 2. processing is completed
total_records_to_process = check_fn(s1, available, completed)

# keep the example running until processing completed
done.wait()

duration = time.time() - t
print(f"processed {total_records_to_process} trust entries in {duration} seconds")
