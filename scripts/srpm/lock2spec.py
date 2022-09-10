#!/usr/bin/env python3

import shutil

import toml
import requests as req
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

    print("BuildRequires:  rust-packaging")
    for r in rpms.values():
        rpm = remappings[r] if r in remappings else r
        print(f"BuildRequires: {rpm}-devel")

    if overridden_crates:
        print("# Overridden to rpms due to Fedora version patching")
        for r in overridden_crates:
            print(f"BuildRequires: rust-{r}-devel")
            unvendor.append(r)

    excluded_crates = overridden_crates + blacklisted_crates
    if vendoring:
        for c in unvendor:
            shutil.rmtree(f"vendor/{c}", ignore_errors=True)
    else:
        i = 1
        for c, v in crates.items():
            if c not in excluded_crates:
                print(f"Source{i}: {v}")
                i += 1

    print(f"Official {len(unvendor)}")
    print(f"Vendored {len(crates) - len(excluded_crates)}")
