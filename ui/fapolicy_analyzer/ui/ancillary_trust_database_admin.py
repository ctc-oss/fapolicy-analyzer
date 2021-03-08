import gi

gi.require_version("Gtk", "3.0")
import os
from gi.repository import Gtk, GLib
from threading import Thread
from time import sleep
from fapolicy_analyzer.app import System
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

        self.trustFileList = TrustFileList(Gtk.FileChooserAction.OPEN)
        self.trustFileList.on_file_selection_change += self.on_file_selection_change
        self.trustFileList.on_database_selection_change += (
            self.on_database_selection_change
        )
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
            else ("T/<b><u>U</u></b>",)
            if s == "u"
            else ("T/U", "light red")
        )

    def __get_trust(self, database):
        sleep(1)
        s = System(None, None, database)
        trust = s.ancillary_trust()
        GLib.idle_add(self.trustFileList.set_trust, trust, self.__status_markup)

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

    def on_database_selection_change(self, database):
        thread = Thread(target=self.__get_trust, args=(database,))
        thread.daemon = True
        thread.start()

    def on_deployBtn_clicked(self, *args):
        deployConfirmDialog = DeployConfirmDialog(
            self.content.get_toplevel()
        ).get_content()
        deployConfirmDialog.run()
        deployConfirmDialog.hide()
