from fapolicy_analyzer import *
import pathlib

# config is loaded from $HOME/.config/fapolicy-analyzer/fapolicy-analyzer.toml
s1 = System()
print(f"system1 has {len(s1.ancillary_trust())} trust entries")

xs = Changeset()
for p in pathlib.Path("/bin").iterdir():
    xs.add_trust(str(p))
print(f"adding {xs.len()} trust entries")

s2 = s1.apply_changeset(xs)
print(f"system2 has {len(s1.ancillary_trust())} trust entries")
for t in s2.ancillary_trust():
    print(f"{t.status} {t.path} {t.size} {t.hash}")
