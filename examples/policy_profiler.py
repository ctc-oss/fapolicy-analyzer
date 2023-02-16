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
import threading
import argparse
import time

import fapolicy_analyzer
from fapolicy_analyzer import *


def main(*argv):
    print(f"v{fapolicy_analyzer.__version__}")

    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs=argparse.REMAINDER)

    parser.add_argument("-r", "--rules", type=str, required=False, help="path to rules")
    parser.add_argument("-d", "--dir", type=str, required=False, help="path to working dir")
    parser.add_argument("--dout", type=str, required=False, help="path to daemon stdout log")
    parser.add_argument("--tout", type=str, required=False, help="path to target(s) stdout log")

    user_opts = parser.add_mutually_exclusive_group(required=False)
    user_opts.add_argument("-u", "--username", type=str, required=False, help="username")
    user_opts.add_argument("--uid", type=int, required=False, help="uid")
    parser.add_argument("-g", "--gid", type=int, required=False, help="gid")

    args = parser.parse_args()

    print(args.target)

    profiler = Profiler()
    wait_for_done = threading.Event()

    def execd(h):
        print(f"[python] executing {h.cmd} ({h.pid})")

    def done():
        print("[python] all done")
        wait_for_done.set()

    profiler.exec_callback = execd
    profiler.done_callback = done

    if args.uid:
        profiler.uid = args.uid

    if args.username:
        profiler.set_user(args.username)

    if args.gid:
        profiler.gid = args.gid

    if args.dout:
        profiler.daemon_stdout = args.dout

    if args.tout:
        profiler.target_stdout = args.tout

    if args.rules:
        profiler.rules = args.rules

    if args.dir:
        profiler.pwd = args.dir

    # profile a single target in a session
    proc_target = profiler.profile(" ".join(args.target))

    time.sleep(5)

    proc_target.kill()

    # profile multiple targets in same session
    #profiler.profile_all(["whoami", "id", "pwd", "ls /tmp"])

    # keep the example running until processing completed
    wait_for_done.wait()


if __name__ == "__main__":
    main(*sys.argv[1:])
