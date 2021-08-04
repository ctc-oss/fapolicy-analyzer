from fapolicy_analyzer import *

# config is loaded from $HOME/.config/fapolicy-analyzer/fapolicy-analyzer.toml
from fapolicy_analyzer.rust import System

s1 = System()
for t in s1.system_trust():
    print(f"{t.path} {t.size} {t.hash}")

print(f"found {len(s1.system_trust())} system trust entries")
