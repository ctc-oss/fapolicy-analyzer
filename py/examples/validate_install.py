import fapolicy_analyzer.syscheck as syscheck
from fapolicy_analyzer import util
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

# validate rpm
syscheck.syscheck_rpm()
