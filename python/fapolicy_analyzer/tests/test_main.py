import context  # noqa: F401
import sys
from unittest.mock import patch
from ui.__main__ import parse_cmdline, gbAutosaveEnabled, gstrEditSessionFileName


def test_parse_args(mocker):
    testargs = ["prog", "-v", "-a", "-s", "/tmp/TmpFileTemplate.tmp"]
    with patch.object(sys, 'argv', testargs):
        args = parse_cmdline()
        print(gbAutosaveEnabled, gstrEditSessionFileName)
        assert args["verbose"]
        assert args["autosave"]
        assert args["session"] == "/tmp/TmpFileTemplate.tmp"
