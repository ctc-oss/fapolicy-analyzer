from fapolicy_analyzer import *

# config is loaded from $HOME/.config/fapolicy-analyzer/fapolicy-analyzer.toml
s1 = System()
for t in s1.ancillary_trust():
    print(f"{t.path} {t.size} {t.hash}")

print(f"found {len(s1.ancillary_trust())} ancillary trust entries")
