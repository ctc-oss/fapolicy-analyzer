from subprocess import SubprocessError
from util.fapd_dbase import fapd_dbase_snapshot


def test_fapd_dbase_snapshot_fails():
    # An unwritable directory should generates a tar failure
    assert not fapd_dbase_snapshot(strArchiveFile="/usr/lib/x.tgz")


def test_fapd_dbase_snapshot_w_exception(mocker):
    # Mock the subprocess.Popen() call to throw an exception
    mocker.patch("subprocess.Popen", side_effect=SubprocessError)
    assert not fapd_dbase_snapshot()
