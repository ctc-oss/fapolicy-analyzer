# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
#
#
# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
import hashlib
import os
import subprocess


def stat(path):
    return subprocess.getoutput(f"stat '{path}'")


def sha(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            sha256 = hashlib.sha256()
            for b in iter(lambda: f.read(4096), b""):
                sha256.update(b)
            return sha256.hexdigest()
