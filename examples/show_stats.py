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

from fapolicy_analyzer import *
import sys
import argparse
import signal
import sys
import threading
from functools import partial

def execd(rec):
    print(f"{rec.summary()}")

def on_sigint(signum, frame, kill):
    print("Terminating...")
    kill()

def main(*argv):
    ss = start_stat_stream("/var/run/fapolicyd/fapolicyd.state", execd)
    wait_for_done = threading.Event()

    handler = partial(
        on_sigint,
        kill=wait_for_done.set,
    )
    signal.signal(signal.SIGINT, handler)
    print("waiting...")
    wait_for_done.wait()


if __name__ == "__main__":
    main(*sys.argv[1:])
