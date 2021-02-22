import fapolicy_analyzer.syscheck as syscheck
from fapolicy_analyzer import util
from fapolicy_analyzer.app import System
from fapolicy_analyzer.svc import Daemon
from fapolicy_analyzer.trust import Trust
from fapolicy_analyzer.util import fs

# validate util library
s = util.example_trust_entry()
ts = s.split(' ')
assert len(ts) == 3
print("- Util library OK")

# validate default Trust stores
s = System(None, None, "tests/data/one.trust")
print(f"- System Trust OK ({len(s.system_trust())})")
print(f"- Ancillary Trust OK ({len(s.ancillary_trust())})")

# validate rpm
syscheck.syscheck_rpm()

# daemon binding
d = Daemon("fakeunit")
print("- Daemon object OK")

# fs utils
stat_str = fs.stat(__file__)
print("- Stat OK")
print(stat_str)
