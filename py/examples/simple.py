import fapolicy_analyzer.trust as fa
from fapolicy_analyzer import util
from fapolicy_analyzer.trust import Trust

s = util.example_trust_entry()
e = fa.parse_trust_entry(s)
print(f"{e.path} {e.size} {e.hash}")

pt = Trust("/home/foo", 100, "hash")
print(f"{pt.path} {pt.size} {pt.hash}")
