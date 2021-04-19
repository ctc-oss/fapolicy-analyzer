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
