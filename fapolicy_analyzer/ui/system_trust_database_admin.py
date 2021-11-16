import logging
import fapolicy_analyzer.ui.strings as strings
from events import Events
from locale import gettext as _
from fapolicy_analyzer.util.format import f
from fapolicy_analyzer.util import fs  # noqa: F401
from .actions import (
    NotificationType,
    add_notification,
    request_system_trust,
)
from .configs import Colors
from .store import dispatch, get_system_feature
from .trust_file_list import TrustFileList
from .trust_file_details import TrustFileDetails
from .ui_widget import UIWidget


class SystemTrustDatabaseAdmin(UIWidget, Events):
    __events__ = ["file_added_to_ancillary_trust"]
    selectedFile = None

    def __init__(self):
        UIWidget.__init__(self)
        Events.__init__(self)
        self._trust = []
        self._error = None
        self._loading = False

        self.trustFileList = TrustFileList(
            trust_func=self.__load_trust, markup_func=self.__status_markup
        )
        self.trustFileList.trust_selection_changed += self.on_trust_selection_changed
        self.get_object("leftBox").pack_start(
            self.trustFileList.get_ref(), True, True, 0
        )

        self.trustFileDetails = TrustFileDetails()
        self.get_object("rightBox").pack_start(
            self.trustFileDetails.get_ref(), True, True, 0
        )

        get_system_feature().subscribe(on_next=self.on_next_system)

    def __status_markup(self, status):
        return (
            ("<b><u>T</u></b>/D", Colors.LIGHT_GREEN)
            if status.lower() == "t"
            else ("T/<b><u>D</u></b>", Colors.LIGHT_RED)
        )

    def __load_trust(self):
        self._loading = True
        dispatch(request_system_trust())

    def on_next_system(self, system):
        trustState = system.get("system_trust")

        if not trustState.loading and self._error != trustState.error:
            self._error = trustState.error
            self._loading = False
            logging.error("%s: %s", strings.SYSTEM_TRUST_LOAD_ERROR, self._error)
            dispatch(
                add_notification(
                    strings.SYSTEM_TRUST_LOAD_ERROR, NotificationType.ERROR
                )
            )
        elif (
            self._loading and not trustState.loading and self._trust != trustState.trust
        ):
            self._error = None
            self._loading = False
            self._trust = trustState.trust
            self.trustFileList.load_trust(self._trust)

    def on_trust_selection_changed(self, trust):
        self.selectedFile = trust
        addBtn = self.get_object("addBtn")
        if trust:
            status = trust.status.lower()
            trusted = status == "t"
            addBtn.set_sensitive(not trusted)

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
            addBtn.set_sensitive(False)

    def on_addBtn_clicked(self, *args):
        if self.selectedFile:
            self.file_added_to_ancillary_trust(self.selectedFile.path)
