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
from fapolicy_analyzer.util import fs  # noqa: F401
from fapolicy_analyzer.util.format import f
from gi.repository import Gdk, Gtk
import os.path

from .actions import (
    NotificationType,
    add_notification,
    apply_changesets,
    request_ancillary_trust,
)
from .ancillary_trust_file_list import AncillaryTrustFileList
from .store import dispatch, get_system_feature
from .trust_file_details import TrustFileDetails
from .remove_deleted_dialog import RemoveDeletedDialog
from .ui_widget import UIConnectedWidget


class AncillaryTrustDatabaseAdmin(UIConnectedWidget):
    def __init__(self):
        super().__init__(get_system_feature(), on_next=self.on_next_system)
        self._changesets = []
        self._trust = []
        self._loading = False
        self.selectedFiles = None

        self.removeMenu = self.__build_remove_deleted_menu()
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
        self.trustFileList.get_object("treeView").connect(
            "button-press-event", self.on_view_button_press_event
        )

    def __build_remove_deleted_menu(self):
        menu = Gtk.Menu()
        removeItem = Gtk.MenuItem.new_with_label("Remove File")
        removeItem.connect("activate", self.on_remove_file_activate)
        menu.append(removeItem)
        menu.show_all()
        return menu

    def __load_trust(self):
        self._loading = True
        dispatch(request_ancillary_trust())

    def __apply_changeset(self, changeset):
        dispatch(apply_changesets(changeset))

    def on_view_button_press_event(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            treeView = self.trustFileList.get_object("treeView")
            model, pathlist = treeView.get_selection().get_selected_rows()
            iter_ = model.get_iter(next(iter(pathlist)))  # single select use first path
            subject = model.get_value(iter_, 3)

            self.removeMenu.popup_at_pointer() if not os.path.isfile(subject.path) else None

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
        self.selectedFiles = [t.path for t in trusts] if trusts else None
        trustBtn = self.get_object("trustBtn")
        untrustBtn = self.get_object("untrustBtn")
        if trusts:
            n_files = len(trusts)
            n_true = sum([True for trust in trusts if getattr(trust, "status", "").lower() == "t"])
            n_false = sum([True for trust in trusts if not getattr(trust, "status", "").lower() == "t"])
            trustBtn.set_sensitive(n_files == n_false)
            untrustBtn.set_sensitive(n_files == n_true)

            trust = trusts[-1]
            status = getattr(trust, "status", "").lower()
            trusted = status == "t"

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
        if self.selectedFiles:
            dne_list = [f for f in self.selectedFiles if not os.path.isfile(f)]
            selectedFiles = [f for f in self.selectedFiles if f not in dne_list]
            if len(dne_list) > 0:
                removeDialog = RemoveDeletedDialog(deleted=dne_list).get_ref()
                resp = removeDialog.run()
                removeDialog.destroy()
                if resp == Gtk.ResponseType.APPLY:
                    self.delete_trusted_files(*dne_list)
                    treeView = self.trustFileList.get_object("treeView")
                    treeView.get_selection().select_path(Gtk.TreePath.new_first())
                    model, pathlist = treeView.get_selection().get_selected_rows()
                    if model:
                        child_model = model.get_model().get_model()
                        iter_ = child_model.get_iter(next(iter(pathlist)))  # single select use first pat
                        child_model.remove(iter_)

            if selectedFiles:
                self.add_trusted_files(*selectedFiles)

    def on_untrustBtn_clicked(self, *args):
        if self.selectedFiles:
            dne_list = [f for f in self.selectedFiles if not os.path.isfile(f)]
            selectedFiles = [f for f in self.selectedFiles if f not in dne_list]
            if len(dne_list) > 0:
                removeDialog = RemoveDeletedDialog(deleted=dne_list).get_ref()
                resp = removeDialog.run()
                removeDialog.destroy()
                if resp == Gtk.ResponseType.APPLY:
                    self.delete_trusted_files(*dne_list)
                    treeView = self.trustFileList.get_object("treeView")
                    treeView.get_selection().select_path(Gtk.TreePath.new_first())
                    model, pathlist = treeView.get_selection().get_selected_rows()
                    if model:
                        child_model = model.get_model().get_model()
                        iter_ = child_model.get_iter(next(iter(pathlist)))  # single select use first pat
                        child_model.remove(iter_)

            if selectedFiles:
                self.delete_trusted_files(*selectedFiles)

    def on_next_system(self, system):
        changesets = system.get("changesets")
        trustState = system.get("ancillary_trust")

        # if changesets have changes request a new ancillary trust
        if self._changesets != changesets:
            self._changesets = changesets
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

    def on_remove_file_activate(self, *args):
        self.delete_trusted_files(*self.selectedFiles)
        treeView = self.trustFileList.get_object("treeView")
        treeView.get_selection().select_path(Gtk.TreePath.new_first())
        model, pathlist = treeView.get_selection().get_selected_rows()
        if model:
            child_model = model.get_model().get_model()
            iter_ = child_model.get_iter(next(iter(pathlist)))  # single select use first pat
            child_model.remove(iter_)
