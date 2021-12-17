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
import subprocess
import os
from util.fs import sha


def test_sha():
    # Create a tmp file
    strTmpFilepath = "/tmp/now_is_the_time.tmp.txt"
    try:
        fp = open(strTmpFilepath, "w")
        fp.write(
            "Now is the time for all good men to come to the aid of " "their country\n"
        )

        # Capture the sha256 hash for path
        strSha256FuncReturn = sha(strTmpFilepath)

        # Independently generate the sha256 hash from a utility for the same path
        strSha256CmdStdout = subprocess.run(
            ["sha256sum", strTmpFilepath], capture_output=True, text=True
        ).stdout.split()[0]
    finally:
        fp.close()
        os.remove(strTmpFilepath)

    assert strSha256FuncReturn == strSha256CmdStdout
