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

import signal
import sys
import threading
from functools import partial

from fapolicy_analyzer import *


def on_sigint(signum, frame, kill):
    print("\rTerminating watcher...")
    kill()


def main(*argv):
    h = Handle("sshd")

    wait_for_done = threading.Event()

    # watch the handle in the background, signal when done
    wh = watch_service_status(h, wait_for_done.set)

    handler = partial(
        on_sigint,
        kill=wh.kill,
    )

    # ctrl+c to kill the watcher
    signal.signal(signal.SIGINT, handler)

    # wait for the watcher thread to exit
    wait_for_done.wait()

    print("done!")


if __name__ == "__main__":
    main(*sys.argv[1:])
