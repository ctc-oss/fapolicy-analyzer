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

import logging
from locale import gettext as _

import fapolicy_analyzer.ui.strings as strings
from fapolicy_analyzer import Changeset, Trust
from fapolicy_analyzer.ui.operations.deploy_changesets_op import DeployChangesetsOp
from fapolicy_analyzer.util import fs  # noqa: F401
from fapolicy_analyzer.util.format import f

from .actions import (
    NotificationType,
    add_notification,
    apply_changesets,
    request_ancillary_trust,
)
from .ancillary_trust_file_list import AncillaryTrustFileList
from .store import dispatch, get_system_feature
from .trust_file_details import TrustFileDetails
from .ui_widget import UIConnectedWidget


class AncillaryTrustDatabaseAdmin(UIConnectedWidget):
    def __init__(self):
        super().__init__(get_system_feature(), on_next=self.on_next_system)
        self._changesets = []
        self._trust = []
        self._loading = False
        self.selectedFile = None

        self.trustFileList = AncillaryTrustFileList(trust_func=self.__load_trust)
        self.trustFileList.trust_selection_changed += self.on_trust_selection_changed
        self.trustFileList.files_added += self.on_files_added
        self.trustFileList.files_deleted += self.on_files_deleted
        self.get_object("leftBox").pack_start(
            self.trustFileList.get_ref(), True, True, 0
        )

        self.trustFileDetails = TrustFileDetails()
        self.get_object("rightBox").pack_start(
            self.trustFileDetails.get_ref(), True, True, 0
        )

        self._deployBtn = self.get_object("deployBtn")

    def __load_trust(self):
        self._loading = True
        dispatch(request_ancillary_trust())

    def __apply_changeset(self, changeset):
        dispatch(apply_changesets(changeset))

    def add_trusted_files(self, *files):
        changeset = Changeset()
        for file in files:
            changeset.add_trust(file)
        self.__apply_changeset(changeset)

    def delete_trusted_files(self, *files):
        changeset = Changeset()
        for file in files:
            changeset.del_trust(file)
        self.__apply_changeset(changeset)

    def on_trust_selection_changed(self, trusts):
        self.selectedFile = trusts if trusts else None
        trustBtn = self.get_object("trustBtn")
        untrustBtn = self.get_object("untrustBtn")
        for trust in trusts:
            if trust:
                status = getattr(trust, "status", "").lower()
                trusted = status == "t"
                trustBtn.set_sensitive(not trusted)
                untrustBtn.set_sensitive(trusted)

                if isinstance(trust, Trust):
                    self.trustFileDetails.set_in_database_view(
                        f(
                            _(
                                """File: {trust.path}
Size: {trust.size}
SHA256: {trust.hash}"""
                            )
                        )
                    )

                self.trustFileDetails.set_on_file_system_view(
                    f(
                        _(
                            """{fs.stat(trust.path)}
SHA256: {fs.sha(trust.path)}"""
                        )
                    )
                )

                self.trustFileDetails.set_trust_status(
                    strings.ANCILLARY_TRUSTED_FILE_MESSAGE
                    if trusted
                    else strings.ANCILLARY_DISCREPANCY_FILE_MESSAGE
                    if status == "d"
                    else strings.ANCILLARY_UNKNOWN_FILE_MESSAGE
                )
            else:
                trustBtn.set_sensitive(False)
                untrustBtn.set_sensitive(False)
                self.trustFileDetails.clear()

    def on_files_deleted(self, files):
        if files:
            self.delete_trusted_files(*files)

    def on_files_added(self, files):
        if files:
            self.add_trusted_files(*files)

    def on_trustBtn_clicked(self, *args):
        if self.selectedFile:
            for sfile in self.selectedFile:
                self.add_trusted_files(sfile.path)

    def on_untrustBtn_clicked(self, *args):
        if self.selectedFile:
            for sfile in self.selectedFile:
                self.delete_trusted_files(sfile.path)

    def on_deployBtn_clicked(self, *args):
        with DeployChangesetsOp(parentWindow=self.get_ref().get_toplevel()) as op:
            op.deploy(self._changesets)

    def on_next_system(self, system):
        changesets = system.get("changesets")
        trustState = system.get("ancillary_trust")

        # if changesets have changes request a new ancillary trust
        if self._changesets != changesets:
            self._changesets = changesets
            self._deployBtn.set_sensitive(len(changesets) != 0)
            self.trustFileList.set_changesets(changesets)
            self.__load_trust()

        # if there was an error loading show appropriate notification
        if trustState.error and self._loading:
            self._loading = False
            logging.error(
                "%s: %s", strings.ANCILLARY_TRUST_LOAD_ERROR, trustState.error
            )
            dispatch(
                add_notification(
                    strings.ANCILLARY_TRUST_LOAD_ERROR, NotificationType.ERROR
                )
            )

        # if not loading and the trust changes reload the view
        if self._loading and not trustState.loading and self._trust != trustState.trust:
            self._loading = False
            self._trust = trustState.trust
            self.trustFileList.load_trust(self._trust)
