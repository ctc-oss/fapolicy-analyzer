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
import os.path
from locale import gettext as _
from typing import Sequence

import fapolicy_analyzer.ui.strings as strings
from fapolicy_analyzer import Trust
from fapolicy_analyzer.ui.changeset_wrapper import Changeset, TrustChangeset
from fapolicy_analyzer.util import fs  # noqa: F401
from fapolicy_analyzer.util.format import f
from gi.repository import Gtk

from fapolicy_analyzer.ui.actions import (
    NotificationType,
    add_notification,
    apply_changesets,
    request_ancillary_trust,
)
from fapolicy_analyzer.ui.ancillary_trust_file_list import AncillaryTrustFileList
from fapolicy_analyzer.ui.remove_deleted_dialog import RemoveDeletedDialog
from fapolicy_analyzer.ui.store import dispatch, get_system_feature
from fapolicy_analyzer.ui.trust_file_details import TrustFileDetails
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget


class AncillaryTrustDatabaseAdmin(UIConnectedWidget):
    def __init__(self):
        super().__init__(get_system_feature(), on_next=self.on_next_system)
        self._changesets: Sequence[Changeset] = []
        self._trust = []
        self._loading = False
        self.selectedFiles = None

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
        self.trustFileList.load_trust(self._trust)
    def __load_trust(self):
        self._loading = True
        dispatch(request_ancillary_trust())

    def __apply_changeset(self, changeset):
        dispatch(apply_changesets(changeset))

    def add_trusted_files(self, *files):
        changeset = TrustChangeset()
        for file in files:
            changeset.add(file)
        self.__apply_changeset(changeset)

    def delete_trusted_files(self, *files):
        changeset = TrustChangeset()
        for file in files:
            changeset.delete(file)
        self.__apply_changeset(changeset)

    def on_trust_selection_changed(self, trusts):
        def is_trustable(trust):
            return getattr(trust, "status", "").lower() == "d"

        def is_untrustable(trust):
            status = getattr(trust, "status", "").lower()
            # unknowns (u) will no longer be an instance of Trust if already deleted
            return status == "t" or (status == "u" and isinstance(trust, Trust))

        self.selectedFiles = [t.path for t in trusts] if trusts else None
        trustBtn = self.get_object("trustBtn")
        untrustBtn = self.get_object("untrustBtn")

        if not trusts:
            trustBtn.set_sensitive(False)
            untrustBtn.set_sensitive(False)
            self.trustFileDetails.clear()
            return

        n_files = len(trusts)
        n_untrustable = sum(is_untrustable(t) for t in trusts)
        n_trustable = sum(is_trustable(t) for t in trusts)

        trustBtn.set_sensitive(n_files == n_trustable)
        untrustBtn.set_sensitive(n_files == n_untrustable)

        trust = trusts[-1]
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

        status = getattr(trust, "status", "").lower()
        self.trustFileDetails.set_trust_status(
            strings.ANCILLARY_TRUSTED_FILE_MESSAGE
            if status == "t"
            else strings.ANCILLARY_DISCREPANCY_FILE_MESSAGE
            if status == "d"
            else strings.ANCILLARY_UNKNOWN_FILE_MESSAGE
        )

    def on_files_deleted(self, files):
        if files:
            self.delete_trusted_files(*files)

    def on_files_added(self, files):
        if files:
            self.add_trusted_files(*files)

    def on_trustBtn_clicked(self, *args):
        if self.selectedFiles:
            self.add_trusted_files(*self.selectedFiles)

    def on_untrustBtn_clicked(self, *args):
        if self.selectedFiles:
            dne_list = [f for f in self.selectedFiles if not os.path.isfile(f)]
            if len(dne_list) > 0:
                removeDialog = RemoveDeletedDialog(deleted=dne_list).get_ref()
                resp = removeDialog.run()
                removeDialog.destroy()
                if resp != Gtk.ResponseType.YES:
                    return

            self.delete_trusted_files(*self.selectedFiles)

    def on_next_system(self, system):
        changesetState = system.get("changesets")
        trustState = system.get("ancillary_trust")

        # if changesets have changes request a new ancillary trust
        if self._changesets != changesetState.changesets:
            self._changesets = changesetState.changesets
            self.trustFileList.set_changesets(self._changesets)
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
