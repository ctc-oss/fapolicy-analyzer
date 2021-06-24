from locale import gettext as _

DEPLOY_ANCILLARY_CONFIRM_DIALOG_TITLE = _("Deploy Ancillary Trust Changes?")
DEPLOY_ANCILLARY_CONFIRM_DIALOG_TEXT = _(
    """Are you sure you wish to deploy your changes to the ancillary trust database?
 This will update the fapolicy trust and restart the service."""
)
DEPLOY_ANCILLARY_CONFIRM_DLG_ACTION_COL_HDR = _("Action")
DEPLOY_ANCILLARY_CONFIRM_DLG_PATH_COL_HDR = _("File Path")

TRUSTED_FILE_MESSAGE = _("This file is trusted.")
DISCREPANCY_FILE_MESSAGE = _("There is a discrepancy with this file.")
UNKNOWN_FILE_MESSAGE = _("The trust status of this file is unknown.")

SYSTEM_TRUST_TAB_LABEL = _("System Trust Database")
ANCILLARY_TRUST_TAB_LABEL = _("Ancillary Trust Database")

FILE_LIST_TRUST_HEADER = _("Trust")
FILE_LIST_FILE_HEADER = _("File")
FILE_LIST_CHANGES_HEADER = _("Changes")
FILE_LIST_MODE_HEADER = _("Mode")
FILE_LIST_ACCESS_HEADER = _("Access")

CHANGESET_ACTION_ADD = _("Add")
CHANGESET_ACTION_DEL = _("Delete")

ADD_FILE_BUTTON_LABEL = _("Add File")

WHITESPACE_WARNING_DIALOG_TITLE = _("File path(s) contains embedded whitespace.")
WHITESPACE_WARNING_DIALOG_TEXT = _(
    "fapolicyd currently does not support paths containing spaces. The following paths will not be added to the "
    + "Trusted Files List.\n(fapolicyd: V TBD)\n\n"
)

LOADER_MESSAGE = _("Loading...")

FILE_LABEL = _("file")
FILES_LABEL = _("files")
USER_LABEL = _("user")
USERS_LABEL = _("users")
GROUP_LABEL = _("group")
GROUPS_LABEL = _("groups")
