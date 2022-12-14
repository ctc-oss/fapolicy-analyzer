import threading
import time

from rx import operators

from fapolicy_analyzer import *
from fapolicy_analyzer.redux import (
  create_store, select_feature
)
from fapolicy_analyzer.ui.actions import system_received
from fapolicy_analyzer.ui.features import SYSTEM_FEATURE, create_system_feature

store = create_store()

t = time.time()
s1 = System()
duration = time.time() - t
print(f"system created in {duration} seconds")

store.add_feature_module(create_system_feature(store.dispatch, s1))
done = threading.Event()


def next_system(system_state):
    system = system_state.get('system').system
    assert len(system.system_trust()) == len(s1.system_trust())
    # print(f"next_system has {s1.system_trust()} system trust entries")


def system_error(e):
    print(f"error: {e}")


def available(updates, pct):
    # merge the updated trust into the system
    s1.merge(updates)
    store.dispatch(system_received(s1))
    print(f"{pct:4}% {len(s1.system_trust())}")


def completed():
    print(f"done")
    done.set()


f = store.as_observable().pipe(operators.map(select_feature(SYSTEM_FEATURE)))
f.subscribe(
    on_next=next_system,
    on_error=system_error,
    on_completed=None,
)

# using the check_disk_trust binding we can set callbacks for when
# 1. new data is available
# 2. processing is completed
check_disk_trust(s1, available, completed)

# keep the example running until processing completed
done.wait()
