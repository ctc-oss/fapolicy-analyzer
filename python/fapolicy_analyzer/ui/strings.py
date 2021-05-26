from locale import gettext as _

DEPLOY_ANCILLARY_CONFIRM_DIALOG_TITLE = _("Deploy Ancillary Trust Changes?")
DEPLOY_ANCILLARY_CONFIRM_DIALOG_TEXT = _(
    """Are you sure you wish to deploy your changes to the ancillary trust database?
 This will update the fapolicy trust and restart the service."""
)

TRUSTED_FILE_MESSAGE = _("This file is trusted.")
DISCREPANCY_FILE_MESSAGE = _("There is a discrepancy with this file.")
UNKNOWN_FILE_MESSAGE = _("The trust status of this file is unknown.")

SYSTEM_TRUST_TAB_LABEL = _("System Trust Database")
ANCILLARY_TRUST_TAB_LABEL = _("Ancillary Trust Database")

FILE_LIST_TRUST_HEADER = _("Trust")
FILE_LIST_FILE_HEADER = _("File")

ADD_FILE_BUTTON_LABEL = _("Add File")

WHITESPACE_WARNING_DIALOG_TITLE = _("File path(s) contains embedded whitespace.")
WHITESPACE_WARNING_DIALOG_TEXT = _(
    "fapolicyd currently does not support paths containing spaces. The following paths will not be added to the "
    + "Trusted Files List.\n(fapolicyd: V TBD)\n\n"
)
