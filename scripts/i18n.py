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
