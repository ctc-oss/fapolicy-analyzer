import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from fapolicy_analyzer.util import fs
from .ui_widget import UIWidget
from .trust_file_list import TrustFileList
from .trust_file_details import TrustFileDetails
from .confirmation_dialog import ConfirmDialog
from .deploy_confirm_dialog import DeployConfirmDialog


class AncillaryTrustDatabaseAdmin(UIWidget):
    def __init__(self, system):
        super().__init__()
        self.content = self.builder.get_object("ancillaryTrustDatabaseAdmin")

        self.trustFileList = TrustFileList(
            trust_func=system.ancillary_trust, markup_func=self.__status_markup
        )
        self.trustFileList.on_file_selection_change += self.on_file_selection_change
        self.builder.get_object("leftBox").pack_start(
            self.trustFileList.get_content(), True, True, 0
        )

        self.trustFileDetails = TrustFileDetails()
        self.builder.get_object("rightBox").pack_start(
            self.trustFileDetails.get_content(), True, True, 0
        )

    def __status_markup(self, status):
        s = status.lower()
        return (
            ("<b><u>T</u></b>/U", "light green")
            if s == "t"
            else ("T/<b><u>U</u></b>", "gold")
            if s == "u"
            else ("T/U", "light red")
        )

    def get_content(self):
        return self.content

    def on_file_selection_change(self, trust):
        if trust:
            self.trustFileDetails.set_in_databae_view(
                f"""File: {trust.path}
Size: {trust.size}
SHA256: {trust.hash}"""
            )
            self.trustFileDetails.set_on_file_system_view(
                f"""{fs.stat(trust.path)}
SHA256: {fs.sha(trust.path)}"""
            )
            status = trust.status.lower()
            self.trustFileDetails.set_trust_status(
                "This file is trusted."
                if status == "t"
                else "This file is untrusted."
                if status == "u"
                else "The trust status of this file is unknown."
            )

    def on_deployBtn_clicked(self, *args):
        parent = self.content.get_toplevel()
        confirmDialog = ConfirmDialog(
            "Deploy Ancillary Trust Changes?",
            "Are you sure you wish to deploy your changes to the ancillary trust database? "
            + "This will update the fapolicy trust and restart the service.",
            parent,
        ).get_content()
        response = confirmDialog.run()
        confirmDialog.hide()
        if response == Gtk.ResponseType.YES:
            deployConfirmDialog = DeployConfirmDialog(parent).get_content()
            deployConfirmDialog.run()
            deployConfirmDialog.hide()
