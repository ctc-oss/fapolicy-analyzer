import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from threading import Thread
from time import sleep
from fapolicy_analyzer.app import System
from fapolicy_analyzer.util import fs
from trust_file_list import TrustFileList
from trust_file_details import TrustFileDetails

systemDb = "/var/lib/rpm"


class SystemTrustDatabaseAdmin:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../glade/system_trust_database_admin.glade")
        self.builder.connect_signals(self)

        self.trustFileList = TrustFileList(
            Gtk.FileChooserAction.SELECT_FOLDER, systemDb
        )
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

    def __build_status_markup(self, status):
        return "<b><u>T</u></b>" if status.lower() == "t" else "T"

    def __get_trust(self, database):
        sleep(1)
        s = System(None, database, None)
        trust = s.system_trust()
        GLib.idle_add(self.trustFileList.set_trust, trust, self.__build_status_markup)

    def get_content(self):
        return self.builder.get_object("systemTrustDatabaseAdmin")

    def on_realize(self, *args):
        if path := self.trustFileList.get_selected_location():
            self.on_database_selection_change(path)

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
