import toml


def required_packages():
    with open('Cargo.lock') as lock:
        packages = toml.load(lock)["package"]
        required = {}
        required_exact = {}
        required_major = {}
        required_minor = {}
        for pkg in packages:
            name = pkg["name"]
            version = pkg["version"]
            (major, minor, patch) = version.split(".", 2)
            if "fapolicy-" in name or "winapi" in name or "wasi" in name:
                continue
            # print(f"{name}={major}.{minor}.{patch}")
            required[name] = version
            required_major[name] = f"{name}:{major}"
            required_minor[name] = f"{name}:{major}.{minor}"
            required_exact[name] = f"{name}:{version}"

        return required, required_exact, required_major, required_minor
