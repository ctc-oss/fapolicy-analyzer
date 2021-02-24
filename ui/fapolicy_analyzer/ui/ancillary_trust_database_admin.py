import gi

gi.require_version("Gtk", "3.0")
import os
from gi.repository import Gtk
from fapolicy_analyzer.app import System
from fapolicy_analyzer.util import fs
from trust_file_list import TrustFileList
from trust_file_details import TrustFileDetails
from deploy_confirm_dialog import DeployConfirmDialog

trustDb = "../../py/tests/data/one.trust"


class AncillaryTrustDatabaseAdmin:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../glade/ancillary_trust_database_admin.glade")
        self.builder.connect_signals(self)
        self.content = self.builder.get_object("ancillaryTrustDatabaseAdmin")

        self.trustFileList = TrustFileList(Gtk.FileChooserAction.OPEN, trustDb)
        self.trustFileList.on_file_selection_change += self.on_file_selection_change
        self.builder.get_object("leftBox").pack_start(
            self.trustFileList.get_content(), True, True, 0
        )

        self.trustFileDetails = TrustFileDetails()
        self.builder.get_object("rightBox").pack_start(
            self.trustFileDetails.get_content(), True, True, 0
        )

    def __build_status_markup(self, status):
        if status.lower() == "t":
            return "<b><u>T</u></b>/U"
        elif status.lower() == "u":
            return "T/<b><u>U</u></b>"

        return "T/U"

    def get_content(self):
        return self.content

    def on_realize(self, *args):
        s = System(None, None, self.trustFileList.get_selected_location())
        trust = s.ancillary_trust()
        trustStore = Gtk.ListStore(str, str, object)
        for i, e in enumerate(trust):
            trustStore.append([self.__build_status_markup(e.status), e.path, e])

        self.trustFileList.set_list_store(trustStore)

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

    def on_deployBtn_clicked(self, *args):
        deployConfirmDialog = DeployConfirmDialog(
            self.content.get_toplevel()
        ).get_content()
        deployConfirmDialog.run()
        deployConfirmDialog.hide()
