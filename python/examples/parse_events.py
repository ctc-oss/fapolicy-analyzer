from fapolicy_analyzer import *

# config is loaded from $HOME/.config/fapolicy-analyzer/fapolicy-analyzer.toml
from fapolicy_analyzer.rust import System

s1 = System()
print(f"found {len(s1.users())} system users")
print(f"found {len(s1.groups())} system groups")

umap = {u.id: u.name for u in s1.users()}
gmap = {g.id: g.name for g in s1.groups()}
for e in s1.events_from("events0.log")[:5]:
    print({"u": umap[e.user()], "g": gmap[e.group()], "s": e.subject(), "o": e.object()})
print("...")
