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

red = "\033[91m"
green = "\033[92m"
yellow = "\033[93m"
blue = "\033[96m"
gray = "\033[33m"


def main(*argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--plain", action="store_true", help="Plain text rules")
    args = parser.parse_args(argv)

    s1 = System()
    print(f"Rule Identity: {rule_identity(s1)}")

    if args.plain:
        print(s1.rules_text())
    else:
        origin = None
        for r in s1.rules():
            if r.origin != origin:
                origin = r.origin
                print()
                print(gray, end="")
                print(f"🗎 [{origin}]\033[0m")

            print(green if r.is_valid else red, end="")
            print(f"{r.id} {r.text} \033[0m")
            for info in r.info:
                marker = f"[{info.category}]" if info.category != "e" else ""
                print(yellow if info.category == "w" else blue, end="")
                print(f"\t- {marker} {info.message} \033[0m")


if __name__ == "__main__":
    main(*sys.argv[1:])
