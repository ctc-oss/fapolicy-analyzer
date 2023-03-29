# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
from locale import gettext as _

from events import Events

import fapolicy_analyzer.ui.strings as strings
from fapolicy_analyzer.ui.actions import (
    NotificationType,
    add_notification,
    request_system_trust,
)
from fapolicy_analyzer.ui.configs import Colors
from fapolicy_analyzer.ui.store import dispatch, get_system_feature
from fapolicy_analyzer.ui.trust_file_details import TrustFileDetails
from fapolicy_analyzer.ui.trust_file_list import TrustFileList
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget
from fapolicy_analyzer.util import fs  # noqa: F401
from fapolicy_analyzer.util.format import f
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


class SystemTrustDatabaseAdmin(UIConnectedWidget, Events):
    __events__ = ["file_added_to_ancillary_trust"]
    selectedFile = None

    def __init__(self):
        UIConnectedWidget.__init__(
            self, get_system_feature(), on_next=self.on_next_system
        )
        Events.__init__(self)
        self.__error = None
        self.__loading = False
        self.__loading_percent = -1

        self.trust_file_list = TrustFileList(
            trust_func=self.__load_trust, markup_func=self.__status_markup
        )
        self.trust_file_list.trust_selection_changed += self.on_trust_selection_changed
        self.get_object("leftBox").pack_start(
            self.trust_file_list.get_ref(), True, True, 0
        )

        self.trustFileDetails = TrustFileDetails()
        self.get_object("rightBox").pack_start(
            self.trustFileDetails.get_ref(), True, True, 0
        )
        self.show_label = False

    def __status_markup(self, status):
        return (
            ("<b><u>T</u></b> / D", Colors.LIGHT_GREEN)
            if status.lower() == "t"
            else ("T / <b><u>D</u></b>", Colors.LIGHT_RED, Colors.WHITE)
        )

    def __load_trust(self):
        self.__loading = True
        self.__loading_percent = -1
        dispatch(request_system_trust())

    def on_next_system(self, system):
        def started_loading(state):
            return (
                self.__loading
                and state.loading
                and state.percent_complete >= 0
                and self.__loading_percent == -1
            )

        def still_loading(state):
            return (
                self.__loading
                and state.loading
                and state.percent_complete > 0
                and self.__loading_percent != state.percent_complete
            )

        def done_loading(state):
            return (
                self.__loading and not state.loading and state.percent_complete >= 100
            )

        trust_state = system.get("system_trust")

        if not trust_state.loading and self.__error != trust_state.error:
            self.__error = trust_state.error
            self.__loading = False
            logging.error("%s: %s", strings.SYSTEM_TRUST_LOAD_ERROR, self.__error)
            dispatch(
                add_notification(
                    strings.SYSTEM_TRUST_LOAD_ERROR, NotificationType.ERROR
                )
            )
        elif started_loading(trust_state):
            self.__error = None
            self.__loading_percent = (
                trust_state.percent_complete if trust_state.percent_complete >= 0 else 0
            )
            self.trust_file_list.set_loading(True)
            self.set_treeview_display() if self.show_label else None
            self.trust_file_list.init_list(trust_state.trust_count)
            self.trust_file_list.append_trust(trust_state.trust)
        elif still_loading(trust_state):
            self.__error = None
            self.__loading_percent = trust_state.percent_complete
            self.trust_file_list.append_trust(trust_state.last_set_completed)
        elif done_loading(trust_state):
            self.__error = None
            self.__loading = False
            self.__loading_percent = 100
            if not self.trust_file_list.show_trusted:
                n_entries = len([data for data in trust_state.trust if data.status.lower() == "u"])
                self.trust_file_list.total = n_entries
                if n_entries == 0:
                    self.set_label_display()

    def set_label_display(self):
        scroll_window = self.trust_file_list.get_object("viewScroll")
        scroll_window.remove(scroll_window.get_child())
        scroll_window.add(Gtk.Label(label=strings.SYSTEM_TRUST_NO_DISCREPANCIES))
        self.show_label = True
        scroll_window.show_all()

    def set_treeview_display(self):
        scroll_window = self.trust_file_list.get_object("viewScroll")
        scroll_window.remove(scroll_window.get_child())
        scroll_window.add(self.trust_file_list.treeView)
        self.show_label = False
        scroll_window.show_all()

    def on_trust_selection_changed(self, trusts):
        self.selectedFiles = trusts
        addBtn = self.get_object("addBtn")
        if trusts:
            n_files = len(trusts)
            n_false = sum([True for trust in trusts if not trust.status.lower() == "t"])
            addBtn.set_sensitive(n_files == n_false)

            trust = trusts[-1]
            status = trust.status.lower()
            trusted = status == "t"

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
                strings.SYSTEM_TRUSTED_FILE_MESSAGE
                if trusted
                else strings.SYSTEM_DISCREPANCY_FILE_MESSAGE
                if status == "d"
                else strings.SYSTEM_UNKNOWN_FILE_MESSAGE
            )
        else:
            addBtn.set_sensitive(False)

    def on_addBtn_clicked(self, *args):
        if self.selectedFiles:
            self.file_added_to_ancillary_trust(
                *[sfile.path for sfile in self.selectedFiles]
            )
