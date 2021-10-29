import pytest
from unittest.mock import MagicMock
import tarfile
import os
import logging
import fnmatch
from fapolicy_analyzer.util.fapd_dbase import (
    fapd_dbase_snapshot,
    fapd_dbase_cleanup_snapshots,
    giBackupFileMaxCount,
    gstrBackupBasename,
)


listCreatedTgzFiles = []


def create_fapd_archive(strFile, mode=None):
    logging.debug(f"create_fapd_archive({strFile})")
    listCreatedTgzFiles.append(strFile)
    return MagicMock(spec=tarfile.TarFile)


def remove_fapd_archive(strFile):
    logging.debug(f"remove_fapd_archive({strFile})")
    listCreatedTgzFiles.remove(strFile)


def delete_fapd_archives():
    listCreatedTgzFiles.clear()


def count_fapd_archives():
    return len(listCreatedTgzFiles)


def glob_fapd_archives(strSearchPattern):
    listReturn = fnmatch.filter(listCreatedTgzFiles, strSearchPattern)
    return listReturn


@pytest.fixture
def manifest():
    """Manifest file contents"""
    strHome = os.environ.get("HOME")
    return f"/var/lib/fapolicyd\n/etc/fapolicyd\n{strHome}/.bashrc"


@pytest.fixture
def tarfile_fs(mocker, manifest):
    mocker.patch("fapolicy_analyzer.util.fapd_dbase.open", read_data=manifest)
    mocker.patch("fapolicy_analyzer.util.fapd_dbase.os.path.isfile", return_value=True)
    mocker.patch("fapolicy_analyzer.util.fapd_dbase.glob.glob",
                 side_effect=glob_fapd_archives)
    mocker.patch(
        "fapolicy_analyzer.util.fapd_dbase.tarfile.open",
        side_effect=create_fapd_archive,
    )
    mocker.patch(
        "fapolicy_analyzer.util.fapd_dbase.os.remove", side_effect=remove_fapd_archive
    )
    mocker.patch("fapolicy_analyzer.util.fapd_dbase.os.path.isfile", return_value=True)


def test_fapd_dbase_snapshot_and_cleanup(mocker, tarfile_fs):
    # Delete all fapd archives in the default location
    delete_fapd_archives()

    # Verify no fapd archives
    assert count_fapd_archives() == 0

    # Create and verify one fapd archive
    assert fapd_dbase_snapshot()
    assert count_fapd_archives() == 1

    # Add another giBackupFileMaxCount+1 of files. Verify max count limit
    # and that all filenames match the default name template
    for i in range(giBackupFileMaxCount + 1):
        assert fapd_dbase_snapshot()
    assert count_fapd_archives() == giBackupFileMaxCount
    assert len(fnmatch.filter(listCreatedTgzFiles,
                              r"*" + gstrBackupBasename + r"_*.tgz")) == giBackupFileMaxCount

    # Clean up: Delete and verify all archives have been removed.
    delete_fapd_archives()
    assert count_fapd_archives() == 0


def test_fapd_dbase_cleanup_snapshots_no_argument():
    assert not fapd_dbase_cleanup_snapshots(None)


def test_fapd_dbase_snapshot_fails():
    # An unwritable directory should generates a tar failure
    assert not fapd_dbase_snapshot(strArchiveFile="/usr/lib/x.tgz")


def test_fapd_dbase_snapshot_w_exception(mocker, tarfile_fs):
    mocker.patch(
        "fapolicy_analyzer.util.fapd_dbase.tarfile.open",
        side_effect=Exception("TarFile exception"),
    )
    assert not fapd_dbase_snapshot()
