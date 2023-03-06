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

import argparse
import signal
import sys
import threading
from functools import partial

from fapolicy_analyzer import Profiler


def on_sigint(signum, frame, kill):
    print("Terminating target...")
    kill()


def main(*argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs=argparse.REMAINDER)

    parser.add_argument("-r", "--rules", type=str, required=False, help="path to rules")
    parser.add_argument("-d", "--dir", type=str, required=False, help="path to working dir")

    user_opts = parser.add_mutually_exclusive_group(required=False)
    user_opts.add_argument("-u", "--username", type=str, required=False, help="username")
    user_opts.add_argument("--uid", type=int, required=False, help="uid")
    parser.add_argument("-g", "--gid", type=int, required=False, help="gid")

    args = parser.parse_args()

    print(args.target)

    profiler = Profiler()
    kill_flag = threading.Event()
    wait_for_done = threading.Event()

    def execd(h):
        print(f"[python] executing {h.cmd} ({h.pid})")

    def done():
        print("[python] all done")
        kill_flag.set()
        wait_for_done.set()

    profiler.exec_callback = execd
    profiler.done_callback = done

    if args.uid:
        profiler.uid = args.uid

    if args.username:
        profiler.user = args.username

    if args.gid:
        profiler.gid = args.gid

    if args.rules:
        profiler.rules = args.rules

    if args.dir:
        profiler.pwd = args.dir

    # profile a single target in a session
    proc_target = profiler.profile(" ".join(args.target))

    handler = partial(
        on_sigint,
        kill=proc_target.kill,
    )

    # ctrl+c to kill the profiling process
    signal.signal(signal.SIGINT, handler)

    # wait for the profiler to exit
    wait_for_done.wait()


if __name__ == "__main__":
    main(*sys.argv[1:])
