from fapolicy_analyzer import *

# config is loaded from $HOME/.config/fapolicy-analyzer/fapolicy-analyzer.toml
s1 = System()
print(f"found {len(s1.users())} system users")
print(f"found {len(s1.groups())} system groups")

umap = {u.id: u.name for u in s1.users()}
gmap = {g.id: g.name for g in s1.groups()}
for e in s1.events_from("events0.log")[:5]:
    print({"u": umap[e.uid],
           "g": gmap[e.gid],
           "s": {
               "file": e.subject.file,
               "trust": e.subject.trust,
               "access": e.subject.access
           },
           "o": {
               "file": e.object.file,
               "trust": e.object.trust,
               "access": e.object.access,
               "mode": e.object.mode
           }})
print("...")
