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

from collections import namedtuple

from fapolicy_analyzer.ui.strings import (
    ANCILLARY_DISCREPANCY_FILE_MESSAGE,
    ANCILLARY_TRUSTED_FILE_MESSAGE,
    ANCILLARY_UNKNOWN_FILE_MESSAGE,
    FILE,
    SIZE,
    SYSTEM_DISCREPANCY_FILE_MESSAGE,
    SYSTEM_TRUSTED_FILE_MESSAGE,
    SYSTEM_UNKNOWN_FILE_MESSAGE,
    UNKNOWN_FILE_MESSAGE,
)
from fapolicy_analyzer.ui.trust_file_details import TrustFileDetails
from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget
from fapolicy_analyzer.util import fs  # noqa: F401

_MESSAGES = {
    "st": {
        "t": SYSTEM_TRUSTED_FILE_MESSAGE,
        "d": SYSTEM_DISCREPANCY_FILE_MESSAGE,
        "unknown": SYSTEM_UNKNOWN_FILE_MESSAGE,
    },
    "at": {
        "t": ANCILLARY_TRUSTED_FILE_MESSAGE,
        "d": ANCILLARY_DISCREPANCY_FILE_MESSAGE,
        "unknown": ANCILLARY_UNKNOWN_FILE_MESSAGE,
    },
    "u": {"unknown": UNKNOWN_FILE_MESSAGE},
}


class TrustReconciliationDialog(UIBuilderWidget):
    def __init__(self, trustObj, databaseTrust=None, parent=None):
        super().__init__()
        if parent:
            self.get_ref().set_transient_for(parent)

        trustFileDetails = self.__load_details(trustObj, databaseTrust)
        self.get_object("content").add(trustFileDetails.get_ref())

    def __load_details(self, trustObj, databaseTrust):
        def set_btn_visibility(trust=False, untrust=False):
            self.get_object("trustBtn").set_visible(trust)
            self.get_object("untrustBtn").set_visible(untrust)

        def get_db_details_or_defaults():
            DBDetails = namedtuple("details", "size, hash, status")
            return (
                DBDetails(
                    databaseTrust.size, databaseTrust.hash, databaseTrust.status.lower()
                )
                if databaseTrust
                else DBDetails(None, None, "unknown")
            )

        trustFileDetails = TrustFileDetails()
        dbDetails = get_db_details_or_defaults()

        trustFileDetails.set_in_database_view(
            f"""{FILE}: {trustObj.file}
{SIZE}: {dbDetails.size or 'Unknown'}
SHA256: {dbDetails.hash or 'Unknown'}"""
        )

        trustFileDetails.set_on_file_system_view(
            f"""{fs.stat(trustObj.file)}
SHA256: {fs.sha(trustObj.file)}"""
        )

        # set status message of file
        trust = trustObj.trust.lower()
        trustMsgs = _MESSAGES.get(trust, _MESSAGES["u"])
        statusMsg = trustMsgs.get(dbDetails.status) or trustMsgs["unknown"]
        trustFileDetails.set_trust_status(statusMsg)

        # set available buttons
        if trust == "st":
            set_btn_visibility(trust=dbDetails.status != "t")
        elif trust == "at":
            set_btn_visibility(
                trust=dbDetails.status != "t", untrust=dbDetails.status == "t"
            )
        else:
            set_btn_visibility(trust=True)

        return trustFileDetails
