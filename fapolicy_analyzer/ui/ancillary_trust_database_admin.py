import gi
import logging
import fapolicy_analyzer.ui.strings as strings
import sys

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from concurrent.futures import ThreadPoolExecutor
from fapolicy_analyzer import Changeset, System, Trust
from locale import gettext as _
from fapolicy_analyzer.util.format import f
from fapolicy_analyzer.util import fs  # noqa: F401
from .ui_widget import UIWidget
from .ancillary_trust_file_list import AncillaryTrustFileList
from .trust_file_details import TrustFileDetails
from .deploy_confirm_dialog import DeployConfirmDialog
from .state_manager import stateManager, NotificationType
from .confirm_info_dialog import ConfirmInfoDialog
from fapolicy_analyzer.util.fapd_dbase import fapd_dbase_snapshot


class AncillaryTrustDatabaseAdmin(UIWidget):
    def __init__(self):
        super().__init__()

        try:
            self.system = System()
        except RuntimeError as e:
            print(e)
            sys.exit(1)

        self.update_system_checkpoint()
        self.executor = ThreadPoolExecutor(max_workers=1)
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

        # To update UI elements, e.g. Deploy button
        stateManager.ev_changeset_queue_updated += self.on_changeset_updated

        # To reapply user trust add/delete requests from opened session file
        stateManager.ev_user_session_loaded += self.on_session_load

    def __load_trust(self, callback):
        def get_trust():
            trust = self.system.ancillary_trust_async()
            GLib.idle_add(callback, trust)

        self.executor.submit(get_trust)

    def __apply_changeset(self, changeset):
        self.system = self.system.apply_changeset(changeset)
        stateManager.add_changeset_q(changeset)
        self.trustFileList.refresh()

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
        # Get list of human-readable undeployed path/operation pairs
        listPathActionTuples = stateManager.get_path_action_list()
        logging.debug(listPathActionTuples)
        parent = self.get_ref().get_toplevel()
        dlgDeployList = ConfirmInfoDialog(parent, listPathActionTuples)
        confirm_resp = dlgDeployList.run()
        dlgDeployList.hide()

        if confirm_resp == Gtk.ResponseType.YES:
            fapd_dbase_snapshot()
            try:
                print("Deploying...")
                self.system.deploy()
                self.update_system_checkpoint()
                stateManager.add_system_notification(
                    strings.DEPLOY_ANCILLARY_SUCCESSFUL_MSG,
                    NotificationType.SUCCESS,
                )
            except RuntimeError as e:
                stateManager.add_system_notification(
                    f"Failed to deploy: {e}",
                    NotificationType.ERROR,
                )
                return

            deployConfirmDialog = DeployConfirmDialog(parent).get_ref()
            revert_resp = deployConfirmDialog.run()
            deployConfirmDialog.hide()
            if revert_resp == Gtk.ResponseType.YES:
                stateManager.del_changeset_q()
            else:
                # TODO: revert here?
                return

    def on_changeset_updated(self):
        deployBtn = self.get_object("deployBtn")
        deployBtn.set_sensitive(stateManager.is_dirty_queue())

    def on_session_load(self, listPaPrs):
        # flake doesn't like long lines so...
        strFunction = "AncillaryTrustAdmin::on_session_load(): "
        logging.debug(strFunction + "{} {}".format(len(listPaPrs), listPaPrs))
        listPath2Add = []
        listPath2Del = []

        for e in listPaPrs:
            logging.debug(e)
            strPath = e[0]
            strAction = e[1]
            if strAction == "Add":
                listPath2Add.append(strPath)
            elif strAction == "Del":
                listPath2Del.append(strPath)
            else:
                print("on_session_load(): Unknown action: {}".format(strAction))

        self.system_rollback_to_checkpoint()
        self.on_files_added(listPath2Add)
        self.on_files_deleted(listPath2Del)

    def system_rollback_to_checkpoint(self):
        self.system = self.system_checkpoint
        return self.system

    def update_system_checkpoint(self):
        self.system_checkpoint = self.get_system()
        return self.system_checkpoint

    def get_system(self):
        if not self.system:
            self.system = System()
        return self.system

    def set_system(self, sys):
        self.system = sys
        return self.system

    def update_system(self):
        self.system = System()
        return self.system
