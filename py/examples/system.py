from fapolicy_analyzer.app import System

s = System("/usr/local/data2/dev/code/isis/fapolicy-analyzer/.local/fapolicyd.trust")
s.dump_trust()
