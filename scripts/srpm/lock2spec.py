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
import toml
from bs4 import BeautifulSoup

mirror_url = "https://mirrors.kernel.org/fedora-epel/9/Everything/x86_64/Packages/r/"


def required_packages():
    project_name = "example-rulec"
    with open('Cargo.lock') as lock:
        packages = toml.load(lock)["package"]
        required = {}
        for pkg in packages:
            name = pkg["name"]
            if name != project_name:
                version = pkg["version"]
                required[name] = version
        return required


def available_packages():
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
    parser.add_argument("dist", type=str, help="Target dist")
    parser.add_argument("--vendor_dir", type=str, default="vendor-rs/vendor", help="This needs to stay synched up with the path in vendor-rs.sh")
    args = parser.parse_args()

    args.dist = args.dist.lstrip(".")
    vendoring_all = args.dist == "el8"
    print(f"dist: {args.dist}")
    if vendoring_all:
        print("== vendoring all ==")

    rpms = {}
    crates = {}
    unvendor = []
    available = available_packages()
    for p, v in required_packages().items():
        print(p)
        if p in available:
            (major, minor, patch) = v.split(".", 2)
            (rpm_major, rpm_minor, rpm_patch) = available[p].split(".", 2)

            if v == available[p]:
                print(f"[official] {p}: exact match {v}")
                rpms[p] = f"rust-{p}"
                unvendor.append(p)
            elif f"{major}.{minor}" == f"{rpm_major}.{rpm_minor}":
                print(f"[official] {p} {v}: patch miss {rpm_patch}")
                rpms[p] = f"rust-{p}"
                unvendor.append(p)
            elif f"{major}" == f"{rpm_major}":
                print(f"[vendor] {p} {v}: minor miss {rpm_minor}")
                rpms[p] = f"rust-{p}"
                unvendor.append(p)
            else:
                print(f"[vendor] {p} {v}: major miss {rpm_major}")
                crates[p] = f"%{{crates_source {p} {v}}}"
        else:
            print(f"[vendor] {p} {v}: not available")
            crates[p] = f"%{{crates_source {p} {v}}}"

    if vendoring_all:
        print(f"Vendored (all) {len(rpms) + len(crates)}")
    else:
        for c in unvendor:
            print(f"[unvendor] {c}")
            shutil.rmtree(f"{args.vendor_dir}/{c}")

        print(f"Official {len(unvendor)}")
        print(f"Vendored {len(crates)}")
