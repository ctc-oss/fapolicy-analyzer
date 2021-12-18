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
import os
import pathlib

import sys


def main(*argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="File or dir to add to trust")
    args = parser.parse_args(argv)

    if not os.path.exists(args.path):
        raise ValueError(f"{args.path} does not exist")

    s = System()
    xs = Changeset()
    if os.path.isdir(args.path):
        for p in pathlib.Path(args.path).iterdir():
            xs.add_trust(str(p))
    else:
        xs.add_trust(args.path)
    s.apply_changeset(xs).deploy()


if __name__ == "__main__":
    main(*sys.argv[1:])
