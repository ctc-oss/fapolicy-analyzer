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
RULES_FILE_READ_ERROR = _("Error reading the Rules file")
RULES_CHANGESET_PARSE_ERROR = _(
    "Error parsing the rules text. See log for more details."
)
RULES_VALIDATION_ERROR = _(
    "The current rule text is not valid and cannot be saved. See Status Information for details."
)
RULES_VALIDATION_WARNING = _(
    "The current rule text has warnings. See Status Information for details."
)
RULE_LABEL = _("Rule")
RULES_LABEL = _("Rules")
DAEMON_INITIALIZATION_ERROR = _("Error initializing communications with daemon")


DEPLOY_ANCILLARY_CONFIRM_DLG_ACTION_COL_HDR = _("Action")
DEPLOY_ANCILLARY_CONFIRM_DLG_CHANGE_COL_HDR = _("Change")
DEPLOY_SYSTEM_SUCCESSFUL_MSG = _("Changes successfully deployed.")
DEPLOY_SYSTEM_ERROR_MSG = _(
    "An error occurred trying to deploy the changes. Please try again."
)
REVERT_SYSTEM_SUCCESSFUL_MSG = _("Successfully reverted to the previous state.")

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
FILE_LIST_RULE_ID_HEADER = _("Rule")

CHANGESET_ACTION_ADD = _("Add")
CHANGESET_ACTION_DEL = _("Delete")
CHANGESET_ACTION_ADD_TRUST = _("Add Trust")
CHANGESET_ACTION_DEL_TRUST = _("Delete Trust")
CHANGESET_ACTION_RULES = _("Edit Rules")

ADD_FILE_LABEL = _("Add File")
OPEN_FILE_LABEL = _("Open File")
SAVE_AS_FILE_LABEL = _("Save As...")
FA_SESSION_FILES_FILTER_LABEL = _("FA Session files")
FA_ARCHIVE_FILES_FILTER_LABEL = _("fapolicyd archive files")
ANY_FILES_FILTER_LABEL = _("Any files")

FAPD_DBUS_START_ERROR_MSG = _("On-line fapolicyd start failed")
FAPD_DBUS_STOP_ERROR_MSG = _("On-line fapolicyd stop failed")

FAPROFILER_TGT_EUID_CHOWN_ERROR_MSG = _("Profiling target file chown failure")
FAPROFILER_TGT_POPEN_ERROR_MSG = _("Profiling target Popen failure")
FAPROFILER_TGT_REDIRECTION_ERROR_MSG = _("Profiling target redirection failure")

PROF_ARG_OK = _("Profiler Session arguments are valid")
PROF_ARG_EXEC_EMPTY = _("Executable field is empty")
PROF_ARG_EXEC_DOESNT_EXIST = _(": file does not exist")
PROF_ARG_EXEC_NOT_EXEC = _(": file is not executable")
PROF_ARG_EXEC_NOT_FOUND = _(": command not found")
PROF_ARG_USER_DOESNT_EXIST = _(": user does not exist")
PROF_ARG_PWD_DOESNT_EXIST = _(": working directory does not exist")
PROF_ARG_PWD_ISNT_DIR = _(": working directory is not a directory")
PROF_ARG_ENV_VARS_FORMATING = _(": env vars not formatted as CSV K=V pairs")
PROF_ARG_ENV_VARS_NAME_BAD = _("Unsupprted env variable name")
PROF_ARG_UNKNOWN = _("Error: Unknown Profiler Session arguments")

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

RESOURCE_LOAD_FAILURE_DIALOG_TEXT = _("Could not load application resources")
RESOURCE_LOAD_FAILURE_DIALOG_ADD_TEXT = _(
    """The required application resource files could not be loaded from disk.
The fapolicy analyzer application cannot open.

Some possible reasons for this failure:

1. Incorrect user permissions on the application resource directory.

2. An incorrectly configured fapolicyd rule set."""
)

TRUST_DB_READ_FAILURE_DIALOG_TITLE = _("Trust Database")
TRUST_DB_READ_FAILURE_DIALOG_TEXT = _(
    """
The fapolicyd trusted resources database
could not be opened and/or read or the rule file(s)
location is incorrectly specified.

Typical reasons for this failure:

1. The user does not have read permissions to access
the database directory or its contents.
[Default: /var/lib/fapolicyd]

2. The database does not exist or was not initialized.

Either the fapolicyd daemon package has not been
installed or if installed, has not been executed. The first
execution of the fapolicyd daemon will create and
populate the trust database.

3. The rule file(s) location is incorrectly specified in
$(HOME)/.config/fapolicy-analyzer/fapolicy-analyzer.toml
    """
)

APPLY_CHANGESETS_ERROR_MESSAGE = _("Error applying changes")

SYNC_FIFO_ERROR_MESSAGE = _("fifo pipe does not exist.\n Default: /run/fapolicyd/fapolicyd.fifo")
