#!/usr/bin/env python3

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
import argparse
import shutil

import requests as req
import tomli
from bs4 import BeautifulSoup

mirror_url = "https://mirrors.kernel.org/fedora-epel/9/Everything/x86_64/Packages/r/"


def required_packages():
    fapolicy_prefix = "fapolicy-"
    with open('Cargo.lock', 'rb') as lock:
        packages = tomli.load(lock)["package"]
        required = {}
        for pkg in packages:
            name = pkg["name"]
            if not name.startswith(fapolicy_prefix):
                version = pkg["version"]
                required[name] = version
        return required


def epel_packages():
    soup = BeautifulSoup(req.get(mirror_url).text, features="html.parser")
    links = soup.find_all('a')

    pkgs = {}
    for link in links:
        if link.text.startswith("rust-"):
            try:
                # rust-zstd-safe-devel-4.1.4-2.fc37.src.rpm
                (name, version) = link.text.split("-", 1)[1].rsplit("-", 1)[0].rsplit("-", 1)
            except:
                continue

            pkgs[name.rstrip("-devel")] = version
    return pkgs


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--vendor_all", action='store_true', help="Vendor all requirements")
    parser.add_argument("--vendor_dir", type=str, default="vendor-rs/vendor", help="This needs to stay synched up with the path in vendor-rs.sh")
    args = parser.parse_args()

    if args.vendor_all:
        print("== vendoring all ==")

    rpms = {}
    crates = {}
    unvendor = []
    epel = epel_packages()
    for p, v in required_packages().items():
        crate_string = f"{p}-{v}"
        #print(f"requirement: {crate_string}")

        if not p in epel and not f"{p}+default" in epel:
            print(f"[vendor] {p} {v}: not available")
            crates[p] = f"%{{crates_source {p} {v}}}"
            continue

        (major, minor, patch) = v.split(".", 2)
        epel_version = epel.get(p) or epel[f"{p}+default"]
        (epel_major, epel_minor, epel_patch) = epel_version.split(".", 2)

        if v == epel_version:
            #print(f"[official] {p}: exact match {v}")
            rpms[p] = f"rust-{p}"
            unvendor.append(crate_string)
        elif f"{major}.{minor}" == f"{epel_major}.{epel_minor}":
            #print(f"[official] {p} {v}: patch miss {epel_patch}")
            rpms[p] = f"rust-{p}"
            unvendor.append(f"{p}-{v}")
        elif f"{major}" == f"{epel_major}":
            #print(f"[vendor] {p} {v}: minor miss {epel_minor}")
            rpms[p] = f"rust-{p}"
            unvendor.append(f"{p}-{v}")
        else:
            print(f"[vendor] {p} {v}: major miss {epel_major}")
            crates[p] = f"%{{crates_source {p} {v}}}"

    if args.vendor_all:
        print(f"Vendored (all) {len(rpms) + len(crates)}")
    else:
        for c in unvendor:
            shutil.rmtree(f"{args.vendor_dir}/{c}")
            #print(f"[unvendor] {c}")

        print(f"Official {len(unvendor)}")
        print(f"Vendored {len(crates)}")
