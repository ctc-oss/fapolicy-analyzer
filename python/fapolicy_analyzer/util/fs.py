import hashlib
import subprocess


def stat(path):
    return subprocess.getoutput(f"stat \'{path}\'")


def sha(path):
    with open(path, "rb") as f:
        sha256 = hashlib.sha256()
        for b in iter(lambda: f.read(4096), b''):
            sha256.update(b)
        return sha256.hexdigest()
