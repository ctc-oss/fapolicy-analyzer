from fapolicy_analyzer import *

# stateful for any unit name
d = Handle("fapolicyd")
print(d.is_active())

# or statically for the default fapolicyd service
print(is_fapolicyd_active())
