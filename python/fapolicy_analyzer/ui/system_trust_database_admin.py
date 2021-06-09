import gi
import ui.strings as strings

gi.require_version("Gtk", "3.0")
from gi.repository import GLib
from events import Events
from concurrent.futures import ThreadPoolExecutor
from fapolicy_analyzer import System
from locale import gettext as _
from fapolicy_analyzer.util.format import f
from fapolicy_analyzer.util import fs  # noqa: F401
from .trust_file_list import TrustFileList
from .trust_file_details import TrustFileDetails
from .ui_widget import UIWidget
from .configs import Colors


class SystemTrustDatabaseAdmin(UIWidget, Events):
    __events__ = ["file_added_to_ancillary_trust"]
    selectedFile = None

    def __init__(self):
        UIWidget.__init__(self)
        Events.__init__(self)
        self.system = System()
        self.executor = ThreadPoolExecutor(max_workers=1)

        self.trustFileList = TrustFileList(
            trust_func=self.__load_trust,
            markup_func=self.__status_markup,
            read_only=True,
        )
        self.trustFileList.file_selection_change += self.on_file_selection_change
        self.get_object("leftBox").pack_start(
            self.trustFileList.get_content(), True, True, 0
        )

        self.trustFileDetails = TrustFileDetails()
        self.get_object("rightBox").pack_start(
            self.trustFileDetails.get_content(), True, True, 0
        )

    def __status_markup(self, status):
        return (
            ("<b><u>T</u></b>/D", Colors.LIGHT_GREEN)
            if status.lower() == "t"
            else ("T/<b><u>D</u></b>", Colors.LIGHT_RED)
        )

    def __load_trust(self, callback):
        def get_trust():
            trust = self.system.system_trust_async()
            GLib.idle_add(callback, trust)

        self.executor.submit(get_trust)

    def get_content(self):
        return self.get_object("systemTrustDatabaseAdmin")

    def on_file_selection_change(self, trust):
        self.selectedFile = trust
        addBtn = self.get_object("addBtn")
        if trust:
            status = trust.status.lower()
            trusted = status == "t"
            addBtn.set_sensitive(not trusted)

            self.trustFileDetails.set_in_databae_view(
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
            addBtn.set_sensitive(False)

    def on_addBtn_clicked(self, *args):
        if self.selectedFile:
            self.file_added_to_ancillary_trust(self.selectedFile.path)
