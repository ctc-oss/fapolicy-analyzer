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


def main(*argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--count", action='store_true', help="only show the count")
    args = parser.parse_args(argv)

    # config is loaded from $HOME/.config/fapolicy-analyzer/fapolicy-analyzer.toml
    s1 = System()

    if args.count:
        print(len(s1.ancillary_trust()))
    else:
        for t in s1.ancillary_trust():
            print(f"{t.path} {t.size} {t.hash}")
        print(f"found {len(s1.ancillary_trust())} ancillary trust entries")


if __name__ == "__main__":
    main(*sys.argv[1:])
