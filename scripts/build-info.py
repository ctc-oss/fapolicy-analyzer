#!/usr/bin/env python3

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
import os
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", type=str, default="fapolicy_analyzer/resources/build-info.json", help="Path to write output")
parser.add_argument("--os", action='store_true', help="Add OS info")
parser.add_argument("--git", action='store_true', help="Add Git info")
parser.add_argument("--time", action='store_true', help="Add build time")
parser.add_argument("--overwrite", action='store_true', help="Overwrite build-info (default append)")

args = parser.parse_args()

if not os.path.exists(args.output) and args.overwrite:
    print(f"build-info.json not found at {args.output}")
    exit(1)

data = {}
if not args.overwrite and os.path.exists(args.output):
    with open(args.output, "r") as f:
        data = json.load(f)

if args.os:
    data["os_info"] = subprocess.getoutput("uname -nr")
if args.git:
    data["git_info"] = subprocess.getoutput("git rev-list HEAD -n1")
if args.time:
    data["time_info"] = subprocess.getoutput("date")

with open(args.output, "w") as f:
    json.dump(data, f, indent=4)
    print(data)


