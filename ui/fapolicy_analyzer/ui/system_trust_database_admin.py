import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from fapolicy_analyzer.app import System
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
        self.trustFileList.on_list_selection_change += (
            self.on_trust_list_selection_change
        )
        self.builder.get_object("leftBox").pack_start(
            self.trustFileList.get_content(), True, True, 0
        )

        self.trustFileDetails = TrustFileDetails()
        self.builder.get_object("rightBox").pack_start(
            self.trustFileDetails.get_content(), True, True, 0
        )

    def get_content(self):
        return self.builder.get_object("systemTrustDatabaseAdmin")

    def on_realize(self, *args):
        s = System(None, self.trustFileList.get_selected_location(), None)
        trust = s.system_trust()
        trustStore = Gtk.ListStore(str, str, object)
        for i, e in enumerate(trust):
            trustStore.append([e.status, e.path, e])

        self.trustFileList.set_list_store(trustStore)

    def on_trust_list_selection_change(self, trust):
        if trust:
            self.trustFileDetails.set_In_Database_View(
                f"""File: {trust.path}
Size: {trust.size}
SHA256: {trust.hash}
"""
            )
