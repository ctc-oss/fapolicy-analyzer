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
