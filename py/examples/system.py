from fapolicy_analyzer.app import System

s = System(None, None, "tests/data/one.trust")
for pt in s.ancillary_trust():
    print(f"{pt.status} {pt.path} {pt.size} {pt.hash}")
