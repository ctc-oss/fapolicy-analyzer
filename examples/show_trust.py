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

from fapolicy_analyzer import *
import argparse
import sys
from datetime import datetime


def main(*argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("trust_type", nargs="+", choices=["system", "file"], help="trust type to show")
    parser.add_argument("-c", "--count", action='store_true', help="only show the count")
    parser.add_argument("-t", "--time", action='store_true', help="show last modified time")
    args = parser.parse_args(argv)

    # config is loaded from $HOME/.config/fapolicy-analyzer/fapolicy-analyzer.toml
    s1 = System()

    for tt in args.trust_type:
        if tt == "system":
            ts = s1.system_trust()
        else:
            ts = s1.ancillary_trust()

        if args.count:
            print(len(ts))
        else:
            for t in ts:
                print(f"{t.path} {t.size} {t.hash}")
                if args.time:
                    if t.actual:
                        formatted = datetime.fromtimestamp(t.actual.last_modified)
                        print(f"\tlast modified: {formatted}")
                        if t.actual.size != t.size:
                            print("\tsize mismatch")
                        if t.actual.hash != t.hash:
                            print("\thash mismatch")
                    else:
                        print("\tfile not found")
            print(f"found {len(ts)} {tt} trust entries")


if __name__ == "__main__":
    main(*sys.argv[1:])
