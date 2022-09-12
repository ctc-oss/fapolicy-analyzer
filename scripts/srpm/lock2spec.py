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
import os
import shutil
import sys

import requests as req
import toml
from bs4 import BeautifulSoup

rawhide_rust = "https://mirrors.kernel.org/fedora/development/rawhide/Everything/source/tree/Packages/r/"

# todo;; try to fit everything in to remappings
overridden_crates = ["paste", "indoc"]
blacklisted_crates = ["paste-impl", "indoc-impl", "parking_lot", "parking_lot_core"]
remappings = {
    "rust-time": "rust-time0.1",
    "rust-arrayvec": "rust-arrayvec0.5"
}


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
    soup = BeautifulSoup(req.get(rawhide_rust).text, features="html.parser")
    links = soup.find_all('a')

    pkgs = {}
    for link in links:
        if link.text.startswith("rust-"):
            try:
                # rust-zstd-safe-4.1.4-2.fc37.src.rpm
                (name, version) = link.text.split("-", 1)[1].rsplit("-", 1)[0].rsplit("-", 1)
            except:
                continue

            pkgs[name] = version
    return pkgs


if __name__ == '__main__':
    vendoring = True
    os_id = None
    os_version = None
    with open("/etc/os-release") as file:
        release = {}
        for ln in file.readlines():
            ln = ln.replace('"', "").strip("\n")
            if len(ln):
                k, v = ln.split("=")
                release[k] = v
        os_id = release.get("ID") or "unknown"
        os_version = release["VERSION_ID"]
    print(f"{os_id}:{os_version}")

    rpms = {}
    crates = {}
    unvendor = []
    available = available_packages()
    for p, v in required_packages().items():
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

    excluded_crates = overridden_crates + blacklisted_crates
    if False:
        print("BuildRequires: rust-packaging")
        for r in rpms.values():
            rpm = remappings[r] if r in remappings else r
            print(f"BuildRequires: {rpm}-devel")

        if overridden_crates:
            print("# Overridden to rpms due to Fedora version patching")
            for r in overridden_crates:
                print(f"BuildRequires: rust-{r}-devel")
                unvendor.append(r)

        for c in unvendor:
            print(f"[unvendor] {c}")
            shutil.rmtree(f"vendor/{c}", ignore_errors=True)
        print(f"Official {len(unvendor)}")
        print(f"Vendored {len(crates) - len(excluded_crates)}")
    else:
        print("BuildRequires: rust-toolset")
        print(f"Vendored (all) {len(rpms) + len(crates) - len(excluded_crates)}")
