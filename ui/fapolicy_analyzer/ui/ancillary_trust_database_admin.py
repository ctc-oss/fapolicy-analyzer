import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from fapolicy_analyzer.util import fs
from trust_file_list import TrustFileList
from trust_file_details import TrustFileDetails
from deploy_confirm_dialog import DeployConfirmDialog


class AncillaryTrustDatabaseAdmin:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../glade/ancillary_trust_database_admin.glade")
        self.builder.connect_signals(self)
        self.content = self.builder.get_object("ancillaryTrustDatabaseAdmin")

        self.trustFileList = TrustFileList(markup_func=self.__status_markup)
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
            self.trustFileDetails.set_In_Database_View(
                f"""File: {trust.path}
Size: {trust.size}
SHA256: {trust.hash}"""
            )
            self.trustFileDetails.set_On_File_System_View(
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
        deployConfirmDialog = DeployConfirmDialog(
            self.content.get_toplevel()
        ).get_content()
        deployConfirmDialog.run()
        deployConfirmDialog.hide()
