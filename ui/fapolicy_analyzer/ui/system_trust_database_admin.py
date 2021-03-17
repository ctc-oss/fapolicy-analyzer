import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from fapolicy_analyzer.app import System
from fapolicy_analyzer.util import fs
from .trust_file_list import TrustFileList
from .trust_file_details import TrustFileDetails
from .ui_widget import UIWidget

systemDb = "/var/lib/rpm"


class SystemTrustDatabaseAdmin(UIWidget):
    def __init__(self):
        super().__init__()

        self.trustFileList = TrustFileList(
            locationAction=Gtk.FileChooserAction.SELECT_FOLDER,
            defaultLocation=systemDb,
            trust_func=lambda x: System(None, x, None).system_trust(),
            markup_func=self.__status_markup,
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
        return (
            ("<b><u>T</u></b>", "light green")
            if status.lower() == "t"
            else ("T", "light red")
        )

    def get_content(self):
        return self.builder.get_object("systemTrustDatabaseAdmin")

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
            self.trustFileDetails.set_trust_status(
                f"This file is {'trusted' if trust.status.lower() == 't' else 'untrusted'}."
            )
