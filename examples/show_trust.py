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
        ts = []
        if tt == "system":
            ts = s1.system_trust()
        else:
            ts = s1.ancillary_trust()

        if args.count:
            print(len(ts))
        else:
            for t in ts:
                print(f"{t.path} {t.size} {t.hash}")
                if args.t:
                    formatted = datetime.fromtimestamp(t.last_modified)
                    print(f"\t-last modified: {formatted}")
            print(f"found {len(ts)} {tt} trust entries")


if __name__ == "__main__":
    main(*sys.argv[1:])
