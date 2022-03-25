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

from locale import gettext as _

FILE = _("FILE")
SIZE = _("SIZE")

SYSTEM_INITIALIZATION_ERROR = _("Error initializing System")
ANCILLARY_TRUST_LOAD_ERROR = _("Error loading Ancillary Trust")
SYSTEM_TRUST_LOAD_ERROR = _("Error loading System Trust")
RULES_LOAD_ERROR = _("Error loading Rules")
RULES_TEXT_LOAD_ERROR = _("Error loading Rules text")
DAEMON_INITIALIZATION_ERROR = _("Error initializing communications with daemon")

DEPLOY_ANCILLARY_CONFIRM_DIALOG_TITLE = _("Deploy Ancillary Trust Changes?")
DEPLOY_ANCILLARY_CONFIRM_DIALOG_TEXT = _(
    """Are you sure you wish to deploy your changes to the ancillary trust database?
 This will update the fapolicy trust and restart the service."""
)
DEPLOY_ANCILLARY_CONFIRM_DLG_ACTION_COL_HDR = _("Action")
DEPLOY_ANCILLARY_CONFIRM_DLG_PATH_COL_HDR = _("File Path")
DEPLOY_ANCILLARY_SUCCESSFUL_MSG = _("Changes successfully deployed.")
DEPLOY_ANCILLARY_ERROR_MSG = _(
    "An error occurred trying to deploy the changes. Please try again."
)

SYSTEM_TRUSTED_FILE_MESSAGE = _("This file is trusted in the System Trust Database.")
SYSTEM_DISCREPANCY_FILE_MESSAGE = _(
    "There is a discrepancy between this file and the System Trust Database."
)
SYSTEM_UNKNOWN_FILE_MESSAGE = _(
    "The trust status of this file is unknown in the System Trust Database."
)

ANCILLARY_TRUSTED_FILE_MESSAGE = _(
    "This file is trusted in the Ancillary Trust Database."
)
ANCILLARY_DISCREPANCY_FILE_MESSAGE = _(
    "There is a discrepancy between this file and the Ancillary Trust Database."
)
ANCILLARY_UNKNOWN_FILE_MESSAGE = _(
    "The trust status of this file is unknown in the Ancillary Trust Database."
)

UNKNOWN_FILE_MESSAGE = _("The trust status of this file is unknown")

SYSTEM_TRUST_TAB_LABEL = _("System Trust Database")
ANCILLARY_TRUST_TAB_LABEL = _("Ancillary Trust Database")

FILE_LIST_TRUST_HEADER = _("Trust")
FILE_LIST_FILE_HEADER = _("File")
FILE_LIST_MTIME_HEADER = _("MTime")
FILE_LIST_CHANGES_HEADER = _("Changes")
FILE_LIST_MODE_HEADER = _("Mode")
FILE_LIST_ACCESS_HEADER = _("Access")

CHANGESET_ACTION_ADD = _("Add")
CHANGESET_ACTION_DEL = _("Delete")

ADD_FILE_LABEL = _("Add File")
OPEN_FILE_LABEL = _("Open File")
SAVE_AS_FILE_LABEL = _("Save As...")
FA_SESSION_FILES_FILTER_LABEL = _("FA Session files")
FA_ARCHIVE_FILES_FILTER_LABEL = _("fapolicyd archive files")
ANY_FILES_FILTER_LABEL = _("Any files")

WHITESPACE_WARNING_DIALOG_TITLE = _("File path(s) contains embedded whitespace.")
WHITESPACE_WARNING_DIALOG_TEXT = _(
    "fapolicyd currently does not support paths containing spaces. The following paths will not be added to the "
    + "Trusted Files List.\n(fapolicyd: V TBD)\n\n"
)

AUTOSAVE_ACTION_DIALOG_TEXT = _(
    """
        Restore your prior session now?

    Yes: Immediately loads your prior session

    No: Continue starting fapolicy-analyzer.

        Your prior session will still be available
        and can be loaded at any point during
        this current session by invoking 'Restore'
        under the 'File' menu.

        """
)

AUTOSAVE_RESTORE_ERROR_MSG = _(
    "An error occurred trying to restore a prior autosaved edit session"
)

LOADER_MESSAGE = _("Loading...")

FILE_LABEL = _("file")
FILES_LABEL = _("files")
USER_LABEL = _("user")
USERS_LABEL = _("users")
GROUP_LABEL = _("group")
GROUPS_LABEL = _("groups")
PARSE_EVENT_LOG_ERROR_MSG = _(
    "An error occurred trying to parse the event log file. Please try again or select a different file."
)
GET_USERS_ERROR_MSG = _(
    "An error occurred trying to retrieve the user list. Please try again."
)
GET_GROUPS_LOG_ERROR_MSG = _(
    "An error occurred trying to retrieve the group list. Please try again."
)

TRUST_DB_READ_FAILURE_DIALOG_TITLE = _("Trust Database")
TRUST_DB_READ_FAILURE_DIALOG_TEXT = _(
    """
The fapolicyd trusted resources database
could not be opened and/or read.

Typical reasons for this failure:

1. The user does not have read permissions to access
the database directory or its contents.
[Default: /var/lib/fapolicyd]

2. The database does not exist or was not initialized.

Either the fapolicyd daemon package has not been
installed or if installed, has not been executed. The first
execution of the fapolicyd daemon will create and
populate the trust database.
    """
)
