import requests as req
from bs4 import BeautifulSoup


def available_packages(prefix: str):
    c = prefix[0]
    soup = BeautifulSoup(req.get(f"https://mirrors.kernel.org/fedora/development/rawhide/Everything/source/tree/Packages/{c}/").text)
    links = soup.find_all('a')

    available = {}
    available_exact = {}
    available_major = {}
    available_minor = {}
    for link in links:
        if link.text.startswith("rust-1.6") or "rust-fbthrift_codegen" in link.text or "rust-packaging-22" in link.text or "rust-srpm-macros" in link.text:
            continue
        if link.text.startswith(prefix):
            if link.text.startswith("py") and not link.text.startswith("python-"):
                print(f"----> {link.text}")
                continue

            # print(link.text)
            # rust-zstd-safe-4.1.4-2.fc37.src.rpm
            (name, version) = link.text.split("-", 1)[1].rsplit("-", 1)[0].rsplit("-", 1)
            available[name] = version
            # print(f"{link.text} - {name} - {version}")
            splits = version.split(".", 2)
            try:
                (major, minor, patch) = splits if len(splits) == 3 else (splits[0], splits[1], 0)
            except:
                continue
            available_major[name] = f"{name}:{major}"
            available_minor[name] = f"{name}:{major}.{minor}"
            available_exact[name] = f"{name}:{version}"
            # print(f"{name}={version}")

    return available, available_exact, available_major, available_minor
