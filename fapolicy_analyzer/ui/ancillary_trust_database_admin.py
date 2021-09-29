import gi
import logging
import fapolicy_analyzer.ui.strings as strings

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from fapolicy_analyzer import Changeset, Trust
from locale import gettext as _
from fapolicy_analyzer.util import fs  # noqa: F401
from fapolicy_analyzer.util.format import f
from fapolicy_analyzer.util.fapd_dbase import fapd_dbase_snapshot
from .actions import (
    apply_changesets,
    add_notification,
    clear_changesets,
    NotificationType,
    request_ancillary_trust,
    deploy_ancillary_trust,
    set_system_checkpoint,
)
from .ancillary_trust_file_list import AncillaryTrustFileList
from .confirm_info_dialog import ConfirmInfoDialog
from .deploy_confirm_dialog import DeployConfirmDialog
from .store import dispatch, get_system_feature
from .trust_file_details import TrustFileDetails
from .ui_widget import UIWidget


class AncillaryTrustDatabaseAdmin(UIWidget):
    def __init__(self):
        super().__init__()
        self._changesets = []
        self._trust = []
        self._deploying = False
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

        get_system_feature().subscribe(on_next=self.on_next_system)

    def __load_trust(self):
        self._loading = True
        dispatch(request_ancillary_trust())

    def __apply_changeset(self, changeset):
        dispatch(apply_changesets(changeset))

    def __display_deploy_confirmation_dialog(self):
        parent = self.get_ref().get_toplevel()
        deployConfirmDialog = DeployConfirmDialog(parent).get_ref()
        revert_resp = deployConfirmDialog.run()
        deployConfirmDialog.hide()
        if revert_resp == Gtk.ResponseType.YES:
            dispatch(set_system_checkpoint())
            dispatch(clear_changesets())
        else:
            # TODO: revert here?
            return

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

    def on_trust_selection_changed(self, trust):
        self.selectedFile = trust.path if trust else None
        trustBtn = self.get_object("trustBtn")
        untrustBtn = self.get_object("untrustBtn")
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
                strings.TRUSTED_FILE_MESSAGE
                if trusted
                else strings.DISCREPANCY_FILE_MESSAGE
                if status == "d"
                else strings.UNKNOWN_FILE_MESSAGE
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
            self.add_trusted_files(self.selectedFile)

    def on_untrustBtn_clicked(self, *args):
        if self.selectedFile:
            self.delete_trusted_files(self.selectedFile)

    def on_deployBtn_clicked(self, *args):
        def changesets_to_path_action_pairs(changesets):
            """Converts to list of human-readable undeployed path/operation pairs"""
            return [t for e in changesets for t in e.get_path_action_map().items()]

        listPathActionTuples = changesets_to_path_action_pairs(self._changesets)
        logging.debug(listPathActionTuples)
        parent = self.get_ref().get_toplevel()
        dlgDeployList = ConfirmInfoDialog(parent, listPathActionTuples)
        confirm_resp = dlgDeployList.run()
        dlgDeployList.hide()

        if confirm_resp == Gtk.ResponseType.YES:
            bSaveFapolicydState = dlgDeployList.get_save_state()
            logging.debug("Save fapolicyd data = {}".format(bSaveFapolicydState))
            if bSaveFapolicydState:
                # Invoke a file chooser dlg and generate the fapd state tarball
                if strArchiveName := self.display_save_fapd_archive_dlg(parent):
                    fapd_dbase_snapshot(strArchiveName)

            logging.debug("Deploying...")
            self._deploying = True
            dispatch((deploy_ancillary_trust()))

    def on_next_system(self, system):
        changesets = system.get("changesets")
        trustState = system.get("ancillary_trust")

        # if changesets have changes request a new ancillary trust
        if self._changesets != changesets:
            self._changesets = changesets
            self._deployBtn.set_sensitive(len(changesets) != 0)
            self.trustFileList.set_changesets(changesets)
            self.__load_trust()

        # if there was an error check if we were loading or deploying and show appropriate notification
        if trustState.error:
            if self._loading:
                self._loading = False
                logging.error(
                    "%s: %s", strings.ANCILLARY_TRUST_LOAD_ERROR, trustState.error
                )
                dispatch(
                    add_notification(
                        strings.ANCILLARY_TRUST_LOAD_ERROR, NotificationType.ERROR
                    )
                )
            elif self._deploying:
                self._deploying = False
                logging.error(
                    "%s: %s", strings.DEPLOY_ANCILLARY_ERROR_MSG, trustState.error
                )
                dispatch(
                    add_notification(
                        strings.DEPLOY_ANCILLARY_ERROR_MSG, NotificationType.ERROR
                    )
                )

        # if not loading and the trust changes reload the view
        if self._loading and self._trust != trustState.trust:
            self._loading = False
            self._trust = trustState.trust
            self.trustFileList.load_trust(self._trust)

        # if not deploying and we were deploying then confirm
        if self._deploying and trustState.deployed:
            self._deploying = False
            dispatch(
                add_notification(
                    strings.DEPLOY_ANCILLARY_SUCCESSFUL_MSG,
                    NotificationType.SUCCESS,
                )
            )
            self.__display_deploy_confirmation_dialog()

    # ########## Fapd backup ########
    def display_save_fapd_archive_dlg(self, parent):
        """Display a file chooser dialog to specify the output archive file."""
        logging.debug("atda::display_save_fapd_archive_dlg()")

        # Display file chooser dialog
        fcd = Gtk.FileChooserDialog(
            strings.SAVE_AS_FILE_LABEL,
            parent,
            Gtk.FileChooserAction.SAVE,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE,
                Gtk.ResponseType.OK,
            ),
        )

        self.__apply_tgz_file_filters(fcd)
        fcd.set_do_overwrite_confirmation(True)
        response = fcd.run()
        fcd.hide()

        strFilename = None
        if response == Gtk.ResponseType.OK:
            strFilename = fcd.get_filename()
            logging.debug(
                f"fadp_dbase::display_save_fapd_archive_dlg::strFilename = {strFilename}"
            )

        fcd.destroy()
        return strFilename

    def __apply_tgz_file_filters(self, dialog):
        fileFilterTgz = Gtk.FileFilter()
        fileFilterTgz.set_name(strings.FA_ARCHIVE_FILES_FILTER_LABEL)
        fileFilterTgz.add_pattern("*.tgz")
        dialog.add_filter(fileFilterTgz)

        fileFilterAny = Gtk.FileFilter()
        fileFilterAny.set_name(strings.ANY_FILES_FILTER_LABEL)
        fileFilterAny.add_pattern("*")
        dialog.add_filter(fileFilterAny)
