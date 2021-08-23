import subprocess
import os
from fapolicy_analyzer.util.fs import sha


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
