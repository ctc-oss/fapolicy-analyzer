import sys
from fapolicy_analyzer import *

for e in parse_audit_log(sys.argv[1]):
    print(f"-- {e}")
