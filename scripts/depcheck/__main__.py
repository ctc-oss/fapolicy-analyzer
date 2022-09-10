import rs
import py
from rawhide import available_packages


def diff(availables, required_fn):
    available, available_exact, available_major, available_minor = availables
    required, required_exact, required_major, required_minor = required_fn()

    print(f"Required packages: {len(required)}")

    lhs = set(required_exact.values())
    rhs = set(available_exact.values())
    exact = lhs - rhs
    print(f"Misses: {len(exact)}")

    lhs = set(required.keys())
    rhs = set(available.keys())
    package = lhs - rhs
    print(f"Not available: {len(package)}")
    for a in package:
        print(f"\t{a}")

    lhs = set(required_major.values())
    rhs = set(available_major.values())
    major = lhs - rhs
    print(f"Major version misses: {len(major) - len(package)}")
    for a in major:
        if a.split(":")[0] not in package:
            print(f"\t{a}")

    lhs = set(required_minor.values())
    rhs = set(available_minor.values())
    minor = lhs - rhs
    print(f"Minor version misses: {len(minor)}")
    for a in minor:
        print(f"\t{a}")


print("Rust")
print("===============")
diff(available_packages("rust"), rs.required_packages)
print()
print("Python")
print("===============")
diff(available_packages("py"), py.required_packages)
