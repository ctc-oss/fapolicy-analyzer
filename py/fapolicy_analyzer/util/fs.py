import subprocess


def stat(path):
    return subprocess.getoutput(f"stat {path}")
