from fapolicy_analyzer import *

# statically check status for the default fapolicyd service
print(is_fapolicyd_active())
stop_fapolicyd()
print(is_fapolicyd_active())
start_fapolicyd()
print(is_fapolicyd_active())

# or control with a stateful handle to any unit by name
d = Handle("fapolicyd")
print(d.is_active)
print(d.stop)
print(d.is_active)
print(d.start)
