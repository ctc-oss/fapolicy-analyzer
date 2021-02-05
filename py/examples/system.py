from fapolicy_analyzer.app import System

s = System("/usr/local/data2/dev/code/isis/fapolicy-analyzer/.local/fapolicyd.trust", None)

# dump the trust store
for pt in s.trust():
    print(f"{pt.path} {pt.size} {pt.hash}")

# or
# s.dump_trust()
