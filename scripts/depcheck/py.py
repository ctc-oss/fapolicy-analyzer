import json

def required_packages():
    with open('Pipfile.lock') as lock:
        lock_json = json.load(lock)
        packages = lock_json["default"]
        packages.update(lock_json["develop"])

        required = {}
        required_exact = {}
        required_major = {}
        required_minor = {}
        for name, pkg in packages.items():
            version = pkg["version"].strip("==")
            splits = version.split(".", 2)
            (major, minor, patch) = splits if len(splits) == 3 else (splits[0], splits[1], 0)
        #     if "fapolicy-" in name or "winapi" in name or "wasi" in name:
        #         continue
        #     print(f"{name}={major}.{minor}.{patch}")
            required[name] = version
            required_major[name] = f"{name}:{major}"
            required_minor[name] = f"{name}:{major}.{minor}"
            required_exact[name] = f"{name}:{version}"

        return required, required_exact, required_major, required_minor
