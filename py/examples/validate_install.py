import fapolicy_analyzer.syscheck as syscheck
from fapolicy_analyzer import util
from fapolicy_analyzer.app import System
from fapolicy_analyzer.svc import Daemon
from fapolicy_analyzer.trust import Trust

# validate util library
s = util.example_trust_entry()
ts = s.split(' ')
assert len(ts) == 3
print("- Util library OK")

# validate Trust object
pt = Trust(ts[0], int(ts[1]), ts[2])
assert pt.path == ts[0]
assert pt.size == int(ts[1])
assert pt.hash == ts[2]
print("- Trust object OK")

# validate Trust stores
s = System("../tests/data/fapolicyd.trust", None)
print(f"- System Trust OK ({len(s.system_trust())})")
print(f"- Ancillary Trust OK ({len(s.ancillary_trust())})")

# validate rpm
syscheck.syscheck_rpm()

# daemon binding
d = Daemon("fakeunit")
print("- Daemon object OK")
