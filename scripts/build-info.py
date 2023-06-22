# Copyright Concurrent Technologies Corporation 2023
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import subprocess
import argparse
from os import path

parse = argparse.ArgumentParser()
parse.add_argument("path")
args = parse.parse_args()


os_info = subprocess.getoutput(["uname -nr"])
git_info = subprocess.getoutput(["git log -n 1"])
time_info = subprocess.getoutput("date")


if path.isfile(args.path):
    try:
        f = open(args.path, "r")
        data = json.load(f)
        f.close()
        if "OS_UNKNOWN" in data["os_info"]:
            data["os_info"] = os_info
        if "GIT_UNKNOWN" in data["git_info"]:
            data["git_info"] = git_info
        if "TIME_UNKNOWN" in data["time_info"]:
            data["time_info"] = time_info

        print(data)

        f = open(args.path, "w")
        json.dump(data, f, indent=4)
        f.close()

    except Exception:
        print(f"Could not open {args.path}")



