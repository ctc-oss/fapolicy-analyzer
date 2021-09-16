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
