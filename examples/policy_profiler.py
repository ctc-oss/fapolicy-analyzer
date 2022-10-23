# Copyright Concurrent Technologies Corporation 2021
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

import sys
import argparse
import fapolicy_analyzer
from fapolicy_analyzer import *


def main(*argv):
    print(f"v{fapolicy_analyzer.__version__}")

    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs=argparse.REMAINDER)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")

    user_opts = parser.add_mutually_exclusive_group(required=False)
    user_opts.add_argument("-u", "--username", type=str, required=False, help="username")
    user_opts.add_argument("--uid", type=int, required=False, help="uid")

    args = parser.parse_args()

    print(args.target)

    profiler = Profiler()

    # profile a single target in a session
    profiler.profile(" ".join(args.target))

    # profile multiple targets in same session
    #profiler.profile_all(["whoami", "id", "pwd", "ls /tmp"])


if __name__ == "__main__":
    main(*sys.argv[1:])
