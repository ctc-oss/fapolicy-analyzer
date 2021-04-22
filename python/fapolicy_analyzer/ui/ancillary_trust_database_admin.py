import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from fapolicy_analyzer import Changeset, System
from fapolicy_analyzer.util import fs
from .ui_widget import UIWidget
from .trust_file_list import TrustFileList
from .trust_file_details import TrustFileDetails
from .confirmation_dialog import ConfirmDialog
from .deploy_confirm_dialog import DeployConfirmDialog
from .configs import Colors
from .state_manager import stateManager


class AncillaryTrustDatabaseAdmin(UIWidget):
    def __init__(self):
        super().__init__()
        self.system = System()
        self.content = self.get_object("ancillaryTrustDatabaseAdmin")

        self.trustFileList = TrustFileList(
            trust_func=self.system.ancillary_trust, markup_func=self.__status_markup
        )
        self.trustFileList.file_selection_change += self.on_file_selection_change
        self.trustFileList.files_added += self.on_files_added
        self.get_object("leftBox").pack_start(
            self.trustFileList.get_content(), True, True, 0
        )

        self.trustFileDetails = TrustFileDetails()
        self.get_object("rightBox").pack_start(
            self.trustFileDetails.get_content(), True, True, 0
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

    def get_content(self):
        return self.content

    def add_trusted_files(self, *files):
        changeset = Changeset()
        for f in files:
            changeset.add_trust(f)

        self.system = self.system.apply_changeset(changeset)
        stateManager.add_changeset_q(changeset)
        self.trustFileList.refresh(self.system.ancillary_trust)

    def on_file_selection_change(self, trust):
        trustBtn = self.get_object("trustBtn")
        untrustBtn = self.get_object("untrustBtn")
        if trust:
            status = trust.status.lower()
            trusted = status == "t"
            trustBtn.set_sensitive(not trusted)
            untrustBtn.set_sensitive(trusted)

            self.trustFileDetails.set_in_databae_view(
                f"""File: {trust.path}
Size: {trust.size}
SHA256: {trust.hash}"""
            )

            self.trustFileDetails.set_on_file_system_view(
                f"""{fs.stat(trust.path)}
SHA256: {fs.sha(trust.path)}"""
            )

            self.trustFileDetails.set_trust_status(
                "This file is trusted."
                if trusted
                else "There is a discrepancy with this file."
                if status == "d"
                else "The trust status of this file is unknown."
            )
        else:
            trustBtn.set_sensitive(False)
            untrustBtn.set_sensitive(False)

    def on_files_added(self, files):
        if files:
            self.add_trusted_files(*files)

    def on_deployBtn_clicked(self, *args):
        parent = self.content.get_toplevel()
        confirmDialog = ConfirmDialog(
            "Deploy Ancillary Trust Changes?",
            "Are you sure you wish to deploy your changes to the ancillary trust database? "
            + "This will update the fapolicy trust and restart the service.",
            parent,
        ).get_content()
        confirm_resp = confirmDialog.run()
        confirmDialog.hide()
        if confirm_resp == Gtk.ResponseType.YES:
            deployConfirmDialog = DeployConfirmDialog(parent).get_content()
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
