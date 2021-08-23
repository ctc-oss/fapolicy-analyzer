import subprocess
import time
import os
import glob
import logging
from datetime import datetime as DT
from util.xdg_utils import xdg_data_dir_prefix, xdg_config_dir_prefix

# Module Globals
giBackupFileMaxCount = 3
gstrBackupBasename = "Fapolicyd_Backup"


def fapd_dbase_cleanup_snapshots(strBackupBasename):
    """Delete oldest fapolicyd dbase backup file in default location,
    if greater than giBackupFileMaxCount."""
    logging.debug("fapd_dbase_cleanup_snapshots()")
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
    """Constructs a snapshot filename w/timestamp, populates it with the files
    specified in a config file list, or if it does not exist or is not
    specified, captures a snapshot of the default fapolicyd dbase data and
    config file locations, /var/lib/fapolicy/ and /etc/fapolicyd/ respectively,
    and saving it in $XDG_DATA_HOME/fapolicyd/."""
    logging.debug("fapd_dbase::fapd_dbase_snapshot()")

    # Set the backup archive's name, if not specified, set to the default
    if not strArchiveFile:
        strArchiveBasename = xdg_data_dir_prefix(gstrBackupBasename)
        timestamp = DT.fromtimestamp(time.time()).strftime("%Y%m%d_%H%M%S_%f")
        strArchiveFile = strArchiveBasename + "_" + timestamp + ".tgz"
        print("Fapolicyd backup to: {}".format(strArchiveFile))

    # Set the manifest file path, if not specified use the default
    if not strListFile:
        strListFile = xdg_config_dir_prefix("fapolicy_backup_manifest.txt")

    # Verify the existence/access of the list file, otherwise use default args
    if os.path.isfile(strListFile):
        listTarSourceArgs = ["-T", strListFile]
    else:
        listTarSourceArgs = ["/var/lib/fapolicyd/", "/etc/fapolicyd/"]

    # Build the tar command w/source options to either use the list or defaults
    listTarCmd = ["/usr/bin/tar", "-czf", strArchiveFile] + listTarSourceArgs
    try:
        p = subprocess.Popen(listTarCmd)
        retCode = p.wait()

        # Delete oldest back-up file
        if retCode == 0:
            fapd_dbase_cleanup_snapshots(strArchiveBasename)
            return True
        else:
            # subprocess had failed did not throw an exception
            print("Fapolicyd pre-deploy backup failed: tar had non zero exit")
            return False
    except Exception as e:
        print("Fapolicyd pre-deploy backup failed: ", e)
        return False
