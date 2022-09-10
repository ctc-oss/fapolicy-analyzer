#!/usr/bin/env python3

import os
import subprocess
import sys


def compile_catalog(*argv):
    msgfmt = "msgfmt"
    domain = "fapolicy_analyzer"
    directory = "fapolicy_analyzer/locale"
    lang = "es"

    mo_dir = os.path.join(directory, lang, "LC_MESSAGES")
    po_file = os.path.join(mo_dir, f"{domain}.po")
    mo_file = os.path.join(mo_dir, f"{domain}.mo")

    if not os.path.exists(mo_dir):
        os.makedirs(mo_dir)

    cmd = [msgfmt, po_file, "-o", mo_file]
    subprocess.call(cmd)


if __name__ == "__main__":
    compile_catalog(*sys.argv[1:])
