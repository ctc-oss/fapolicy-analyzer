import fapolicy_analyzer as fa
from fapolicy_analyzer import util

s = util.example_trust_entry()
e = fa.parse_trust_entry(s)
print(f"{e.path} {e.size} {e.hash}")
