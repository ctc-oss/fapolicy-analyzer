from fapolicy_analyzer import *

#
# There are two ways to control a service using the dbus backend components
#

# 1. Static calls that use the default "fapolicyd" service
print(is_fapolicyd_active())
stop_fapolicyd()
print(is_fapolicyd_active())
start_fapolicyd()
print(is_fapolicyd_active())

# 2. Stateful object that takes a unit name
d = Handle("fapolicyd")
print(d.is_active)
print(d.stop)
print(d.is_active)
print(d.start)
