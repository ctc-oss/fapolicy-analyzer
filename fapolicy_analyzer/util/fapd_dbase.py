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

import tarfile
import time
import os
import glob
import logging
from datetime import datetime as DT
from fapolicy_analyzer.util.xdg_utils import (
    app_state_dir_prefix,
    app_config_dir_prefix,
)

# Module Globals
giBackupFileMaxCount = 3
gstrBackupBasename = "Fapolicyd_Backup"


def fapd_dbase_cleanup_snapshots(strBackupBasename):
    """Delete oldest fapolicyd dbase backup file in default location,
    if greater than giBackupFileMaxCount."""
    logging.info("fapd_dbase_cleanup_snapshots()")
    if not strBackupBasename:
        return False

    strSearchPattern = strBackupBasename + "_*.tgz"
    logging.debug("Search Pattern: {}".format(strSearchPattern))
    listBackupFiles = glob.glob(strSearchPattern)
    logging.debug("Glob search results: {}".format(listBackupFiles))
    if listBackupFiles and len(listBackupFiles) >= giBackupFileMaxCount:
        # Sequential ops because these methods work in-place w/no return values
        listBackupFiles.sort()
        listBackupFiles.reverse()

        # Iterate through the oldest files and delete them.
        for f in listBackupFiles[giBackupFileMaxCount:]:
            if os.path.isfile(f):
                logging.debug("Deleting: {}".format(f))
                os.remove(f)


def fapd_dbase_snapshot(strArchiveFile=None, strListFile=None):
    """Constructs a snapshot filename w/timestamp (if not specified),
    populates it with the files specified in a config file list, or if
    it does not exist or is not specified, captures a snapshot of the
    default fapolicyd dbase data and config file locations,
    /var/lib/fapolicy/ and /etc/fapolicyd/ respectively, and saving
    it in $XDG_DATA_HOME/fapolicyd/.

    If archive filename is specified, will not perform cleanup of prior
    autosaved archive files, as this is a user invoked operation.
    """
    logging.info("fapd_dbase::fapd_dbase_snapshot()")

    # Set the backup archive's name, if not specified, set to the default
    if not strArchiveFile:
        strArchiveBasename = app_state_dir_prefix(gstrBackupBasename)
        timestamp = DT.fromtimestamp(time.time()).strftime("%Y%m%d_%H%M%S_%f")
        strArchiveFile = strArchiveBasename + "_" + timestamp + ".tgz"
        print("Fapolicyd backup to: {}".format(strArchiveFile))
    else:
        # If strArchiveFile is specified, do not clean-up autosave files
        strArchiveBasename = None

    # Set the manifest file path, if not specified use the default
    if not strListFile:
        strListFile = app_config_dir_prefix("fapolicy_backup_manifest.txt")

    # Verify the existence/access of the list file, otherwise use default args
    if os.path.isfile(strListFile):
        with open(strListFile) as fileListFile:
            listInput = [e.rstrip() for e in fileListFile]
    else:
        listInput = ["/var/lib/fapolicyd/", "/etc/fapolicyd/"]

    # Use the py tarfile module to creat and populate a tarball
    try:
        with tarfile.open(strArchiveFile, "w:gz") as fileTar:
            for source_dir in listInput:
                fileTar.add(source_dir)

            # Delete oldest back-up file
            fapd_dbase_cleanup_snapshots(strArchiveBasename)
        return True

    except Exception as e:
        print("Fapolicyd pre-deploy backup failed: ", e)
        return False
