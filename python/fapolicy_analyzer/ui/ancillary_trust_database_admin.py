import gi
import ui.strings as strings

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from concurrent.futures import ThreadPoolExecutor
from fapolicy_analyzer import Changeset, System
from locale import gettext as _
from fapolicy_analyzer.util.format import f
from fapolicy_analyzer.util import fs  # noqa: F401
from .ui_widget import UIWidget
from .trust_file_list import TrustFileList
from .trust_file_details import TrustFileDetails
from .deploy_confirm_dialog import DeployConfirmDialog
from .configs import Colors
from .state_manager import stateManager, NotificationType
from .confirm_info_dialog import ConfirmInfoDialog


class AncillaryTrustDatabaseAdmin(UIWidget):
    def __init__(self):
        super().__init__()
        self.system = System()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.selectedFile = None

        self.trustFileList = TrustFileList(
            trust_func=self.__load_trust, markup_func=self.__status_markup
        )
        self.trustFileList.trust_selection_changed += self.on_trust_selection_changed
        self.trustFileList.files_added += self.on_files_added
        self.get_object("leftBox").pack_start(
            self.trustFileList.get_ref(), True, True, 0
        )

        self.trustFileDetails = TrustFileDetails()
        self.get_object("rightBox").pack_start(
            self.trustFileDetails.get_ref(), True, True, 0
        )

        stateManager.changeset_queue_updated += self.on_changeset_updated

    def __status_markup(self, status):
        s = status.lower()
        return (
            ("<b><u>T</u></b>/D", Colors.LIGHT_GREEN)
            if s == "t"
            else ("T/<b><u>D</u></b>", Colors.LIGHT_RED)
            if s == "d"
            else ("T/D", Colors.LIGHT_YELLOW)
        )

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
            status = trust.status.lower()
            trusted = status == "t"
            trustBtn.set_sensitive(not trusted)
            untrustBtn.set_sensitive(trusted)

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

        # TODO: 20210607 tpa Functional verification. Pls leave in until ui
        # element integration
        print(listPathActionTuples)
        parent = self.get_ref().get_toplevel()
        dlgDeployList = ConfirmInfoDialog(parent)
        dlgDeployList.load_path_action_list(stateManager.get_path_action_list())
        confirm_resp = dlgDeployList.run()
        dlgDeployList.hide()

        if confirm_resp == Gtk.ResponseType.YES:
            try:
                self.system.deploy()
            except BaseException:  # BaseException to catch pyo3_runtime.PanicException
                stateManager.add_system_notification(
                    "An error occurred trying to deploy the changes. Please try again.",
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
