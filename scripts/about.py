import json
import subprocess
from os import path


abspath = path.abspath("./data/fapolicy-analyzer-about.json")
os_info = subprocess.getoutput(["uname -nr"])
git_info = subprocess.getoutput(["git log -n 1"])
time_info = subprocess.getoutput("date")

f = open(abspath, "r")
data = json.load(f)
f.close()


if "OS_UNKNOWN" in data["os_info"]:
    data["os_info"] = os_info
if "GIT_UNKNOWN" in data["git_info"]:
    data["git_info"] = git_info
if "TIME_UNKNOWN" in data["time_info"]:
    data["time_info"] = time_info

f = open(abspath, "w")
json.dump(data, f, indent=4)
f.close()

